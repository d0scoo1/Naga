from test_base import *


def test_pauseable():
    set_solc('0.8.1')
    slither = Slither("tests/contracts/pausable.sol")
    cs =  slither.contracts_derived
    for c in cs:
        print(c.name)
        
        for f in c.functions_entry_points:
            print("  ",f.name)
            for state_variable in f.all_state_variables_read():
                print("\t r ",state_variable.name)
            for state_variable in f.all_state_variables_written():
                print("\t w ",state_variable.name)

from naga.core.type_compare import *
from naga.core.function_exp import (FunctionExp,_search_related_nodes,__search_all_related_nodes)
def find_owners():
    set_solc('0.8.1')
    slither = Slither("tests/contracts/owner_1.sol")
    cs =  slither.contracts_derived
    contract = cs[0]
    print(contract.name)

    owners = [] # owner candidates
    
    for sv in contract.state_variables:
        if is_owner_type(sv):
            owners.append(sv)
    
    # 查找所有 write 这些变量的 function
    for sv in owners:
        print()
        print(sv)
        b, dep_state_vars = is_owner(sv)
        #print(sv, is_owner)
        #for d in dep_state_vars:
        #    print("\t",d.name,d.type)
           
def is_owner(svar):
    '''
        判断 state variable 是否是 owner
        
        return: []:返回约束这个 state variable 的 state variables
    '''
    # 找到变量所有相关的写 function
    funs = get_functions_writing_to_variable(svar)
    dep_state_vars = set() # 此变量的所依赖的 state variable
    #判断写 function 是否被 require 或 assert，以及 state var, msg.sender 约束
    for fun in funs:
        print("  ",fun.name)
        if fun.is_constructor:
            continue
        cond_nodes = exp_all_require_or_assert_nodes(fun)

        if len(cond_nodes) == 0: # 没有被约束返回 False
            return False, []
        # 检查每个约束，如果同时包含 state var 和 msg.sender, 则加入到依赖变量中
        for node in cond_nodes:
            
            print('    ',node)
            node_track(node)

        """
        
            state_variables_read = []
            local_variables_read = []
            solidity_variables_read = []
            for rn in __search_all_related_nodes(node):
                print("\t",rn,rn.local_variables_read)
                state_variables_read += rn.state_variables_read
                local_variables_read += rn.local_variables_read
                solidity_variables_read += rn.solidity_variables_read
            if len(local_variables_read) > 0:
                print("依赖外部变量")
                for lv in local_variables_read:
                    print('\t',lv)
            if SolidityVariableComposed('msg.sender') not in solidity_variables_read:
                print("缺少 msg.sender")
            if len(state_variables_read) == 0:
                print("缺少 state variable")
        """
    return True, dep_state_vars


# 污点追踪引擎，从污点开始，找到所有依赖的变量
def node_track(_node):
    '''
        输入一个 node, 根据 node 找到所有依赖的变量
    '''

    #print('---track node---',_node)
    nodes = _node.function.nodes
    while nodes:
        if _node == nodes.pop(): break
    nodes.append(_node)

    #for n in nodes: print("\t",n)

    irs = [ir for node in nodes for ir in node.irs_ssa]
    #for ir in irs: print("\t",ir)

    dep_irs_ssa = irs_ssa_track(irs)
    dep_vars = [] # 是一个三维数组，第一维对应每个变量，第二维对应 sv,lv, solv constant
    print()
    #print('----',_node,_node.variables_read,_node.variables_written)
    for vs in dep_irs_ssa:
        state_vars = set()
        local_vars = set()
        solidity_vars = []
        for v in vs:
            if isinstance(v,StateIRVariable):
                state_vars.add(v)
            elif isinstance(v,LocalIRVariable):
                local_vars.add(v)
            elif isinstance(v,(SolidityVariableComposed,Constant)):
                solidity_vars.append(v)
            else:
                print('未知变量！',v)
        dep_vars.append([list(state_vars),list(local_vars),solidity_vars])

    #for vs in dep_vars: print(vs)
    return dep_vars, dep_irs_ssa


def irs_ssa_track(irs):
    """
        输入一组 irs，从最后一个往上追踪

        首先从 ir.read 中找到读依赖，分别判断，如果是 Constant 或 SolidityVariable 类型，则停止查找直接存入依赖，否则继续查找，直到找不到。
        查找过程为：
            将待查变量放到待查数组中，
            由于每一行都是之前行的依赖，因此查找下一行中是否有赋值，如果有，则使用赋值替换此变量
            遇到 internalcall,则从return 开始，同样查找依赖，并更新。
    """
    #print('-----irs track-----',)
    if len(irs) == 0: return [[]]
    tainted_ir = irs.pop()
    #print('    ',tainted_ir)

    tainted_vars = []
    for r in tainted_ir.read:
        tainted_vars.append([r]) # 二维数组
    while irs:
        ir = irs.pop()
        #print('    ',ir)
        lval = ir.lvalue  # 由于是从 read 开始查找， read 必有左值，所以这里不进行判断
        rval = []
        if isinstance(ir, InternalCall): # 如果是 internalcall
            rval = internalCall_track(ir) # internalCall_track 返回的是一个 [[],[]] 需要转换为 []
            rval =sum(rval,[])
        else:
            rval = ir.read

        # 找到 tainted_vars 中的 lval，使用 rval 替换
        for tvs in tainted_vars:
            t_index = 0
            exisited = False
            for tv in tvs:
                if tv == lval:
                    exisited = True 
                    break
                t_index += 1

            if exisited:
                tvs.pop(t_index) # 删掉旧值
                tvs += rval # 替换
    return tainted_vars
    

from slither.slithir.operations import (
    HighLevelCall,
    Index,
    InternalCall,
    Length,
    LibraryCall,
    LowLevelCall,
    Member,
    OperationWithLValue,
    Phi,
    PhiCallback,
    SolidityCall,
    Return,
    Operation,
)

def internalCall_track(ir):
    #print("-----internalCall_track-----",ir.function)

    irs = [ir for n in ir.function.nodes for ir in n.irs_ssa] # all_nodes()
    if len(irs) == 0: return [[]] # 由于后面使用了 sum([[]],[]),所以这里必须返回二维数组
    last_ir = irs[-1]
    if not isinstance(last_ir, Return): return [[]] # 如果最后一个 ir 不是 return，则直接返回
    return irs_ssa_track(irs) # 直接调用 irs track


def get_functions_writing_to_variable(var: "Variable"):
    return [f for f in var.contract.functions_entry_points if var in f.all_state_variables_written()]

def get_functions_read_to_variable(var: "Variable"):
    return [f for f in var.contract.functions_entry_points if var in f.all_state_variables_read()]

def exp_all_require_or_assert_nodes(fun):
    nodes = [node for node in fun.all_nodes() if node.contains_require_or_assert()]
    return nodes




#if ir.read[i] == SolidityVariableComposed('msg.sender'):

if __name__ == "__main__":
    #test_pauseable()
    find_owners()
