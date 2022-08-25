from typing import List
from slither.core.cfg.node import Node,NodeType
from .variable_group import (VariableGroup,var_group_combine)
from slither.core.declarations import Function
from slither.slithir.operations import (
    HighLevelCall,Index,InternalCall,EventCall,Length,LibraryCall,LowLevelCall,Member,OperationWithLValue,Phi,PhiCallback,SolidityCall,Return,Operation,Condition,Transfer)
from slither.slithir.variables import (
    Constant,
    LocalIRVariable,
    ReferenceVariable,
    StateIRVariable,
    TemporaryVariable,
    TupleVariable,
)
NO_LVALUE_OPERATIONS = (Condition,Return,EventCall,Transfer)
class NodeExp():
    def __init__(self, node:Node, tainted_vars = []):
        self.node = node
        self.tainted_vars = tainted_vars
        self.dep_vars_groups:List[VariableGroup] = node_tracker(self.node,self.tainted_vars)

    def __str__(self):
        return "NodeExp: node:{} vars_group:[{}]".format(self.node,self.read_vars_groups)


class Caller():
    def __init__(self, call_ir, dep_vars:List):
        self.call_ir = call_ir
        self.dest_function = call_ir.function
        self.dest_contract = call_ir.function.contract
        self.dep_vars = dep_vars
        self.dep_vars_groups:VariableGroup = VariableGroup(dep_irs_ssa = dep_vars)

    def local_var_callers(self):
        '''
        return the local variables that are used in the caller
        '''
        vars = [ var for var in self.dep_vars_groups.local_vars if str(var.type).startswith("address")]
        if len(vars) > 0:
            return vars
        else:
            return [var for var in self.dep_vars_groups.local_vars if str(var.type).startswith("bytes")]
    
    def state_var_callers(self):
        '''
        return the state variables that are used in the caller
        '''
        vars = [ var for var in self.dep_vars_groups.state_vars if str(var.type).startswith("address")]
        if len(vars) > 0:
            return vars
        else:
            return [var for var in self.dep_vars_groups.state_vars if str(var.type).startswith("bytes")]

def node_tracker(node:Node, tainted_vars = []):

    # 删掉无关 node
    dom_candidates = node.function.nodes
    while dom_candidates:
        if node == dom_candidates.pop(): break
    dom_candidates.append(node)

    dominators = [n for n in dom_candidates if n.type != NodeType.ENTRYPOINT]
    dom_irs = [ir for node in dominators for ir in node.irs_ssa]
    dep_vars, callers = dep_tracker(tainted_vars,dom_irs,{node.function.full_name})

    return VariableGroup(dep_irs_ssa = dep_vars, callers = callers)


##### Data-dependency Analysis Engine #####

def dep_tracker(tainted_vars = [], dom_irs = [], walked_functions = set(), is_call = False, callers = {}):
    '''
    callers 是一个 dict, key 是 变量名称， value 是一个 variableGroup，记录了调用者的依赖信息
    这里 caller 有两种情况：1.依赖一个 local variable, 这种情况，我们认为是可变的。2. 依赖一个 state variable, 这时，caller 是否可变由这个 svar 的读写来决定
    '''
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
            dep_vars += call_track(ir,dom_irs.copy(),walked_functions,callers)
        else:
            dep_vars += ir.read # 必须写在 walked_function检查前，防止自调用
    return dep_vars, callers

def highLevelCall_dom_tracker(call_ir:HighLevelCall,r_dom_irs, walked_functions,callers):
    #if call_ir.function in walked_functions: return []
    #walked_functions.add(call_ir.function)
    tainted_ir = call_ir.destination
    #print('tainted_ir: {}'.format(tainted_ir))
    dom_vars, t_callers = dep_tracker([tainted_ir],r_dom_irs,walked_functions,True, callers)
    return dom_vars

def call_track(call_ir,r_dom_irs, walked_functions,callers):
    '''
    call_ir: call
    r_dom_irs: rest of dom_ir 还未检测的 irs，用于追踪 call 的调用者
    '''
    dep_vars = []

    # 处理 HighLevelCall 的外部调用情况
    # 查找这个 call 的调用者，下面的这些变量都将受到调用者影响
    dom_caller = None
    if isinstance(call_ir, HighLevelCall) and 'HIGH_LEVEL_CALL' in str(call_ir):
        dom_vars = highLevelCall_dom_tracker(call_ir, r_dom_irs, walked_functions, callers)
        dom_caller = Caller(call_ir, dom_vars)
        #print('dom_caller: {}'.format(dom_caller.call_ir))

    if not isinstance(call_ir.function,Function): return [] # 0x196f4727526ea7fb1e17b2071b3d8eaa38486988  return trustedData.balance(holder);

    dom_irs = [ir for n in call_ir.function.nodes for ir in n.irs_ssa if n.type != NodeType.ENTRYPOINT]

    index = 0
    for ir in dom_irs:
        index += 1
        if isinstance(ir, Return):
            t_dep_vars, t_callers = dep_tracker(ir.read, dom_irs[0:index],walked_functions,True)
            # 这些变量都受到了调用者的影响
            _add_dom_caller(t_dep_vars, dom_caller, callers)
            dep_vars += t_dep_vars
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
                    t_dep_vars, t_callers = dep_tracker([ir.lvalue], dom_irs[0:index],walked_functions,True)
                    _add_dom_caller(t_dep_vars, dom_caller, callers)
                    dep_vars += t_dep_vars
    return dep_vars


def _add_dom_caller(vars,dom_caller,callers):
    if dom_caller is None:
        return
    for var in vars:
        if isinstance(var,(StateIRVariable,LocalIRVariable)):
            if var not in callers:
                callers[var._non_ssa_version] = []
            callers[var._non_ssa_version].append(dom_caller)
    
def list2str(l):
    l = [str(i) for i in l]
    return ','.join(l)