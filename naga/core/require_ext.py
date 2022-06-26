from slither.core.cfg.node import Node
from slither.slithir.operations.binary import (Binary,BinaryType)
from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.mapping_type import MappingType
from slither.core.declarations import SolidityVariableComposed

def get_requires(node:Node) -> list:
    '''
        一个 require 中可能有多个 && 条件，这等价于多个 require，所以依据 require 中的 && 条件分割成多个 require
    '''
    if not any( c.name in ["require(bool)", "require(bool,string)"] for c in node.solidity_calls):
        print("Require node is not a require node")
        return
    
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

    return [RequireEXT(node, rnc, msg) for rnc in r_node_conds]

from .node_ext import NodeEXT

class RequireEXT(NodeEXT):
    def __init__(self, node, condition, msg):
        self.node = node
        self.condition = condition # 每个 require 我们只关心一个 condition
        self.msg = msg # 第二个参数
        super().__init__(node,tainted_vars = [self.condition])
        
        self._owner_candidates = None

    @property
    def owner_candidates(self):
        """
            如果 all_read_vars_group 中 local_vars 为空，state_vars 中有 address 或 mapping(address => bool)，且 solidity_vars 中存在一个 msg.sender，则我们认为它可能是 owner
        """

        if self._owner_candidates is not None:
            return self._owner_candidates

        self._owner_candidates = []

        if len(self.all_read_vars_group.local_vars) > 0 or SolidityVariableComposed('msg.sender') not in self.all_read_vars_group.solidity_vars:
            return self._owner_candidates

        for svar in self.all_read_vars_group.state_vars:
            if svar.type == ElementaryType('address'):
                self._owner_candidates.append(svar)
            elif isinstance(svar.type, MappingType) and svar.type.type_from == ElementaryType('address'): #and svar.type.type_to == ElementaryType('bool'):
                self._owner_candidates.append(svar)
        return self._owner_candidates

    def __str__(self):
        return "RequireNode: {}\nMsg: {}\n{}".format(self.node,self.msg,self.all_read_vars_group)