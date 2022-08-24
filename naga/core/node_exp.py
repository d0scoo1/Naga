from typing import List
from slither.core.cfg.node import Node,NodeType
from .variable_group import (VariableGroup,var_group_combine)
from slither.core.declarations import Function
from slither.slithir.operations import (
    HighLevelCall,Index,InternalCall,EventCall,Length,LibraryCall,LowLevelCall,Member,OperationWithLValue,Phi,PhiCallback,SolidityCall,Return,Operation,Condition,Transfer)

NO_LVALUE_OPERATIONS = (Condition,Return,EventCall,Transfer)
class NodeExp():
    def __init__(self, node:Node, tainted_vars = []):
        self.node = node
        self.tainted_vars = tainted_vars
        self.dep_vars_groups:List[VariableGroup] = node_tracker(self.node,self.tainted_vars)
        #self.all_read_vars_group:VariableGroup = var_group_combine(self.read_vars_groups)

    def __str__(self):
        return "NodeExp: node:{} vars_group:[{}]".format(self.node,self.read_vars_groups)

def node_tracker(node:Node, tainted_vars = []):

    # 删掉无关 node
    dom_candidates = node.function.nodes
    while dom_candidates:
        if node == dom_candidates.pop(): break
    dom_candidates.append(node)

    dominators = [n for n in dom_candidates if n.type != NodeType.ENTRYPOINT]
    dom_irs = [ir for node in dominators for ir in node.irs_ssa]
    dep_vars = dep_tracker(tainted_vars,dom_irs,{node.function.full_name})
    return VariableGroup(dep_irs_ssa = dep_vars)


##### Data-dependency Analysis Engine #####
def dep_tracker(tainted_vars = [], dom_irs = [], walked_functions = set(), is_call = False):
    #for ir in dom_irs: print('ir :{}'.format(ir))
    
    if len(dom_irs) == 0: return []

    if tainted_vars == []:
        t_ir = dom_irs.pop()
        tainted_vars = t_ir.read
    #print('tainted_vars: {}'.format('.'.join(str(i) for i in tainted_vars)))

    dep_vars:List = tainted_vars

    while dom_irs:
        ir = dom_irs.pop()
        
        if isinstance(ir,NO_LVALUE_OPERATIONS): continue
        
        lval = ir.lvalue
        if lval in dep_vars: dep_vars.remove(lval)
        else: continue
        #print(ir, list2str(ir.read))
        if isinstance(ir, (InternalCall,HighLevelCall)):
            #print("----internalcall",ir.function.full_name)
            if not is_call: dep_vars += ir.arguments # 对于首个调用函数，我们把参数也加入到 dep_vars 中
            if ir.function in walked_functions: continue
            walked_functions.add(ir.function)
            dep_vars += call_track(ir,walked_functions)
        else:
            dep_vars += ir.read # 必须写在 walked_function检查前，防止自调用
    return dep_vars

def call_track(call_ir, walked_functions = []):
    dep_vars = []
    if not isinstance(call_ir.function,Function): return [] # 0x196f4727526ea7fb1e17b2071b3d8eaa38486988  return trustedData.balance(holder);

    dom_irs = [ir for n in call_ir.function.nodes for ir in n.irs_ssa if n.type != NodeType.ENTRYPOINT]

    index = 0
    for ir in dom_irs:
        index += 1
        if isinstance(ir, Return):
            dep_vars += dep_tracker(ir.read, dom_irs[0:index],walked_functions,True)
    '''
    对/mnt/c/users/vk/naga/tokens/token20/contracts/0.8.7/0x33db8d52d65f75e4cdda1b02463760c9561a2aa1/OUSD.sol 的扩展

    function _governor() internal view returns (address governorOut) {
        bytes32 position = governorPosition;
        assembly {
            governorOut := sload(position)
        }
    }
    '''

    if len(call_ir.function.returns) > 0:
        for ret_val in call_ir.function.returns:
            if ret_val.name == '':
                continue
            index = 0
            for ir in dom_irs:
                index += 1
                if isinstance(ir,NO_LVALUE_OPERATIONS):
                    continue
                if ir.lvalue is not None and ir.lvalue.non_ssa_version == ret_val:
                    dep_vars += dep_tracker([ir.lvalue], dom_irs[0:index],walked_functions,True)
    return dep_vars

def list2str(l):
    l = [str(i) for i in l]
    return ','.join(l)