from slither.core.cfg.node import Node, NodeType
from slither.slithir.operations.binary import (Binary,BinaryType)
from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.mapping_type import MappingType
from slither.core.declarations import SolidityVariableComposed
from slither.core.variables.variable import Variable
from typing import List

def _get_condition_depVars(node:Node,msg:str,params2agrs) -> List:
    '''
    The condition statement could have more than one condition, connected by AND &&, which is equal to multiple requires.
    We divide the requires into multiple requires by &&.
    '''
    if node.irs_ssa == []:
        return []

    r_vars = []
    l_vars = []

    for ir in node.irs_ssa:
        if isinstance(ir,Binary) and ir.type == BinaryType.ANDAND: # 找到 && 情况，将其拆分为多个 require
            l_vars.append(ir.lvalue) # 保存左值是为了将 read 中依赖的值去掉
            r_vars += ir.read

    r_node_conds = [ v for v in r_vars if v not in l_vars]
    # 如果没有 && 条件，则直接为空
    if len(r_node_conds) != 0: # 存在 && 条件
        return [ConditionNode(node, [rnc], msg, params2agrs) for rnc in r_node_conds] # 设置为多个 require
    else:
        return [ConditionNode(node,node.irs_ssa[-1].read,msg,params2agrs)] #依赖条件直接为require 的 read

def get_require(node:Node,fn) -> List:
    if not any(c.name in ["require(bool)", "require(bool,string)"] for c in node.solidity_calls):
        return []
    
    msg = ''
    read_vars = node.irs_ssa[-1].read
    if len(read_vars) == 2:
        msg = read_vars[1]
    conds = _get_condition_depVars(node,msg,fn.params2agrs)
    if len(conds) > 1: fn.andand_if_nodes.append(node) # 如果有多个 require，则记录下来
    return conds

def get_if(node:Node,fn) -> List:
    if node.type not in [NodeType.IF, NodeType.IFLOOP]:
        return []
    msg = 'if_statement'
    conds = _get_condition_depVars(node,msg,fn.params2agrs)
    if len(conds) > 1: fn.andand_if_nodes.append(node) # 如果有多个 require，则记录下来
    return conds

from slither.slithir.variables import (
    Constant,
    LocalIRVariable,
    ReferenceVariable,
    StateIRVariable,
    TemporaryVariable,
    TupleVariable,
)



from .node_naga import NodeN

class ConditionNode(NodeN):
    def __init__(self, node:Node, condition_read:Variable, msg:str,params2agrs:dict={}):
        self.condType:NodeType = node.type # 使用 node 的 type 作为 condType
        self.condition_read:List = condition_read # 每个 require 我们只关心一个 condition
        self.msg:str = msg # require 还包含一个 message
        super().__init__(node,tainted_vars = self.condition_read,params2agrs=params2agrs)

        self.owner_candidates = self._get_owner_candidates()
    
    def exist_oror(self):
        for ir in self.node.irs_ssa:
            if isinstance(ir,Binary) and ir.type == BinaryType.OROR:
                return True

    def _get_owner_candidates(self):
        """
        如果 dep_vars_groups 中 local_vars 为空，state_vars 中有 address 或 mapping(address => bool)，且 solidity_vars 中存在一个 msg.sender，则我们认为它可能是 owner
        """
        
        if len(self.dep_vars_groups.local_vars) > 0 or SolidityVariableComposed('msg.sender') not in self.dep_vars_groups.solidity_vars:
            return []

        owner_candidates = []
        for svar in self.dep_vars_groups.state_vars:
            if svar.type == ElementaryType('address') or svar.type == ElementaryType('bytes32'):
                owner_candidates.append(svar)

            elif isinstance(svar.type, MappingType) and (svar.type.type_from == ElementaryType('address') or svar.type.type_from == ElementaryType('bytes32')): #and svar.type.type_to == ElementaryType('bool'):
                owner_candidates.append(svar)

        return owner_candidates

    def _print(self):
        return {
            "expression": str(self.node.expression),
            "condition_type": str(self.condType),
            "msg": str(self.msg),
            "state_vars":list(set([str(s) for s in self.dep_vars_groups.state_vars])),
            "local_vars":list(set([str(s) for s in self.dep_vars_groups.local_vars])),
            "solidity_vars":list(set([str(s) for s in self.dep_vars_groups.solidity_vars])),
            "constant_vars":list(set([str(s) for s in self.dep_vars_groups.constant_vars])),
        }
    def __str__(self):
        return "node: {},msg: {}, \n{}".format(self.node,self.msg,self.dep_vars_groups)