from slither.core.cfg.node import Node, NodeType
from slither.slithir.operations.binary import (Binary,BinaryType)
from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.mapping_type import MappingType
from slither.core.declarations import SolidityVariableComposed
from slither.core.variables.variable import Variable
from typing import List


def get_requires(node:Node) -> List:
    '''
    The REQUIRE statement could have more than one condition, connected by AND &&, which is equal to multiple requires.
    We divide the requires into multiple requires by &&.
    '''
    if not any( c.name in ["require(bool)", "require(bool,string)"] for c in node.solidity_calls):
        #print("Require node is not a require node")
        return []
    
    msg = ''
    read_vars = node.irs_ssa[-1].read
    if len(read_vars) == 2:
        msg = read_vars[1]

    r_vars = []
    l_vars = []
    for ir in node.irs_ssa:
        if isinstance(ir,Binary) and ir.type == BinaryType.ANDAND: # 找到 && 情况，将其拆分为多个 require
            l_vars.append(ir.lvalue) # 保存左值是为了将 read 中依赖的值去掉
            r_vars += ir.read
    r_node_conds = list(set(r_vars) - set(l_vars))

    if len(r_node_conds) == 0:
        r_node_conds = [read_vars[0]] # 如果没有 && 条件，则直接使用最后一个 ir 的 read 作为 require

    return [RequireExp(node, rnc, msg) for rnc in r_node_conds]

def get_if(node:Node) -> List:
    if node.type not in [NodeType.IF, NodeType.IFLOOP]:
        return []
    msg = 'if_statement'
    read_vars = node.irs_ssa[-1].read
    r_vars = []
    l_vars = []
    for ir in node.irs_ssa:
        if isinstance(ir,Binary) and ir.type == BinaryType.ANDAND: # 找到 && 情况，将其拆分为多个 require
            l_vars.append(ir.lvalue) # 保存左值是为了将 read 中依赖的值去掉
            r_vars += ir.read
    r_node_conds = list(set(r_vars) - set(l_vars))

    if len(r_node_conds) == 0:
        r_node_conds = [read_vars[0]] # 如果没有 && 条件，则直接使用最后一个 ir 的 read 作为 require
    return [RequireExp(node, rnc, msg) for rnc in r_node_conds]
    



from .node_exp import NodeExp

class RequireExp(NodeExp):
    def __init__(self, node:Node, condition_read:Variable, msg:str):
        self.node:Node = node
        self.condition_read = condition_read # 每个 require 我们只关心一个 condition
        self.msg:str = msg # 第二个参数
        super().__init__(node,tainted_vars = [self.condition_read])
        self.owner_candidates = self._get_owner_candidates()


    def _get_owner_candidates(self):
        """
        如果 all_read_vars_group 中 local_vars 为空，state_vars 中有 address 或 mapping(address => bool)，且 solidity_vars 中存在一个 msg.sender，则我们认为它可能是 owner
        """

        if len(self.all_read_vars_group.local_vars) > 0 or SolidityVariableComposed('msg.sender') not in self.all_read_vars_group.solidity_vars:
            return []

        owner_candidates = []
        for svar in self.all_read_vars_group.state_vars:
            if svar.type == ElementaryType('address') or svar.type == ElementaryType('bytes32'):
                owner_candidates.append(svar)

            elif isinstance(svar.type, MappingType) and (svar.type.type_from == ElementaryType('address') or svar.type.type_from == ElementaryType('bytes32')): #and svar.type.type_to == ElementaryType('bool'):
                owner_candidates.append(svar)

        return owner_candidates

    def _dict(self):
        return {
            "expression": str(self.node.expression),
            "msg": str(self.msg),
            "state_vars":list(set([str(s) for s in self.all_read_vars_group.state_vars])),
            "local_vars":list(set([str(s) for s in self.all_read_vars_group.local_vars])),
            "solidity_vars":list(set([str(s) for s in self.all_read_vars_group.solidity_vars])),
            "constant_vars":list(set([str(s) for s in self.all_read_vars_group.constant_vars])),
        }
    def __str__(self):
        return "node: {},msg: {}, \n{}".format(self.node,self.msg,self.all_read_vars_group)