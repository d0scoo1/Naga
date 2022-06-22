import logging

logger = logging.getLogger()
from .declarations.dep_vars import DepVars
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
from slither.core.declarations import SolidityVariableComposed
from slither.slithir.variables import (
    Constant,
    LocalIRVariable,
    ReferenceVariable,
    StateIRVariable,
    TemporaryVariable,
    TupleVariable,
)
from slither.slithir.operations.binary import (Binary,BinaryType)

def require_split(_node):
    '''
        require 中可能有多个条件由 && 连接，我们对其进行拆分，对于 || 情况，我们不予考虑
    '''
    print(_node)

    r_vars = []
    l_vars = []
    for ir in _node.irs_ssa:
        #print(ir)
        if isinstance(ir,Binary) and ir.type == BinaryType.ANDAND: # 找到 && 情况，将其拆分为多个 require
            l_vars.append(ir.lvalue) # 保存左值是为了将 read 中依赖的值去掉
            r_vars += ir.read
    tainted_vars = list(set(r_vars) - set(l_vars))
    #for t in tainted_vars: print(t)
    
    if tainted_vars == []:
        node_track(_node)
    else:
        for t in tainted_vars:
            logger.info("tainted_vars: {}".format(t))
            node_track(_node,tainted_vars=[[t]])


def node_track(_node, tainted_vars = None):
    '''
        输入一个 node, 根据 node 找到所有依赖的变量
    '''
    logger.info("---- node track {}".format(_node))
    nodes = _node.function.nodes
    while nodes:
        if _node == nodes.pop(): break
    nodes.append(_node)

    for n in nodes: logger.debug("node: {}".format(n))

    irs = [ir for node in nodes for ir in node.irs_ssa]
    for ir in irs: logger.debug("ir  : {}".format(ir))

    dep_irs_ssa = irs_ssa_track(irs,tainted_vars)
    dep_vars = [] # 是一个三维数组，第一维对应每个变量，第二维对应 sv,lv, solv constant

    for vs in dep_irs_ssa:
        print('------------------',vs)
        dep_vars.append(DepVars(dep_irs_ssa = vs))

    return dep_vars

def irs_ssa_track(irs, tainted_vars=None):
    """
        输入一组 irs，从最后一个往上追踪

        首先从 ir.read 中找到读依赖，分别判断，如果是 Constant 或 SolidityVariable 类型，则停止查找直接存入依赖，否则继续查找，直到找不到。
        查找过程为：
            将待查变量放到待查数组中，
            由于每一行都是之前行的依赖，因此查找下一行中是否有赋值，如果有，则使用赋值替换此变量
            遇到 internalcall,则从return 开始，同样查找依赖，并更新。
    """
    logger.info('----irs_ssa_track---- {}')
    if len(irs) == 0: return [[]]

    if tainted_vars is None:
        tainted_vars = []
        tainted_ir = irs.pop()
        logger.debug("  track ir: {}".format(tainted_ir))
        for r in tainted_ir.read:
            tainted_vars.append([r]) # 二维数组
    
    while irs:
        ir = irs.pop()
        logger.debug("  track ir: {}".format(ir))
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

def internalCall_track(ir):
    logger.info("-----internalCall_track----- {}".format(ir.function))


    irs = [ir for n in ir.function.nodes for ir in n.irs_ssa] # all_nodes()
    if len(irs) == 0: return [[]] # 由于后面使用了 sum([[]],[]),所以这里必须返回二维数组
    last_ir = irs[-1]
    if not isinstance(last_ir, Return): return [[]] # 如果最后一个 ir 不是 return，则直接返回
    return irs_ssa_track(irs) # 直接调用 irs track