from typing import List
from slither.core.cfg.node import Node
from .variable_group import (VariableGroup,var_group_combine)
from slither.slithir.operations import (
    HighLevelCall,Index,InternalCall,EventCall,Length,LibraryCall,LowLevelCall,Member,OperationWithLValue,Phi,PhiCallback,SolidityCall,Return,Operation,Condition,Transfer)

NO_LEFT_VALUE_OPERATIONS = (Condition,Return,EventCall,Transfer)
class NodeExp():
    def __init__(self, node:Node, tainted_vars = None):
        self.node = node
        self.tainted_vars = tainted_vars
        self.read_vars_groups:List[VariableGroup] = node_track(self.node,self.tainted_vars)
        self.all_read_vars_group:VariableGroup = var_group_combine(self.read_vars_groups)

    def __str__(self):
        return "NodeExp: node:{} vars_group:[{}]".format(self.node,self.all_read_vars_group)

def node_track(node, tainted_vars = None):
    '''
    Track all relevant variables of a node.
    '''
    nodes = node.function.nodes
    while nodes:
        if node == nodes.pop(): break
    nodes.append(node)

    irs = [ir for node in nodes for ir in node.irs_ssa]
    if tainted_vars is not None: tainted_vars = [[c] for c in tainted_vars]
    dep_irs_ssa = irs_ssa_track(irs,tainted_vars)

    return [VariableGroup(dep_irs_ssa = vs) for vs in dep_irs_ssa] # 将每个 irs_ssa 转为 DepVars

def irs_ssa_track(irs, tainted_vars=None):
    """
    Input a list of irs, track from the last ir.

    首先从 ir.read 中找到读依赖，分别判断，如果是 Constant 或 SolidityVariable 类型，则停止查找直接存入依赖，否则继续查找，直到找不到。
    查找过程为：
        将待查变量放到待查数组中，
        由于每一行都是之前行的依赖，因此查找下一行中是否有赋值，如果有，则使用赋值替换此变量
        遇到 internalcall,则从return 开始，同样查找依赖，并更新。
    """

    if len(irs) == 0: return []

    tainted_ir = None
    if tainted_vars is None:
        tainted_vars = []
        tainted_ir = irs.pop()
        for r in tainted_ir.read:
            tainted_vars.append([r]) # 二维数组
    else:
        tainted_ir = irs.pop()

    from_functions = set()
    from_functions.add(tainted_ir.function.full_name)
    while irs:
        ir = irs.pop()
        if isinstance(ir,NO_LEFT_VALUE_OPERATIONS): #,PhiCallback,SolidityCall,LibraryCall,LowLevelCall,HighLevelCall
            continue
        try:
            lval = ir.lvalue
        except:
            print(ir,type(ir))
        lval = ir.lvalue  # 由于是从 read 开始查找， read 必有左值，所以这里不进行判断
        rval = []
        if isinstance(ir, InternalCall): # 如果是 internalcall
            #print("----internalcall",ir,from_function)
            rval = internalCall_track(ir,from_functions) # internalCall_track 返回的是一个 [[],[]] 需要转换为 []
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


def internalCall_track(t_ir,from_functions=set()):
    """
        from_function: 防止循环调用
    """
    irs = [ir for n in t_ir.function.nodes for ir in n.irs_ssa] # all_nodes()
    if len(irs) == 0: return [] # 由于后面使用了 sum([[]],[]),所以这里必须返回二维数组
    rvals = []
    index = 0
    for ir in irs:
        index += 1
        if isinstance(ir, Return) and ir.function.full_name not in from_functions:
            rvals += sum(irs_ssa_track(irs[0:index]),[])
    if rvals != []:
        return rvals
    
    '''
        对于/mnt/c/users/vk/naga/tokens/token20/contracts/0.8.7/0x33db8d52d65f75e4cdda1b02463760c9561a2aa1/OUSD.sol 的扩展

        function _governor() internal view returns (address governorOut) {
        bytes32 position = governorPosition;
        assembly {
            governorOut := sload(position)
        }
    }
    '''
    if len(t_ir.function.returns) > 0: # TMP_67(uint256) = SOLIDITY_CALL sload(uint256)(position_1)
        for ret_val in t_ir.function.returns:
            if ret_val.name == '':
                continue
            index = 0
            for ir in irs:
                index += 1
                if isinstance(ir,NO_LEFT_VALUE_OPERATIONS):
                    continue
                if ir.lvalue is not None and ir.lvalue.non_ssa_version == ret_val and ir.function.full_name not in from_functions:
                    rvals += sum(irs_ssa_track(irs[0:index]),[])

    return rvals

"""
def internalCall_track(ir):
    
    irs = [ir for n in ir.function.nodes for ir in n.irs_ssa] # all_nodes()
    if len(irs) == 0: return [] # 由于后面使用了 sum([[]],[]),所以这里必须返回二维数组
    rval = []

    index = 0
    for ir in irs:
        index += 1
        if isinstance(ir, Return):
           rval += sum(irs_ssa_track(irs[0:index]),[])
    return rval
"""