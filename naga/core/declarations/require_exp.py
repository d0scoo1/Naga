from slither.core.cfg.node import Node
from slither.slithir.operations.binary import (Binary,BinaryType)


from slither.slithir.operations import (
    HighLevelCall,Index,InternalCall,Length,LibraryCall,LowLevelCall,Member,OperationWithLValue,Phi,PhiCallback,SolidityCall,Return,Operation,)
from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.mapping_type import MappingType
from slither.core.declarations import SolidityVariableComposed

from .variable_group import (VariableGroup,var_group_combine)


def get_requires(node) -> list:
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

    return [RequireExp(node, rnc, msg) for rnc in r_node_conds]

from .node_exp import NodeExp
class RequireExp(NodeExp):
    def __init__(self, node, condition, msg):
        self.node = node
        self.condition = condition # 每个 require 我们只关心一个 condition
        self.msg = msg # 第二个参数
        super().__init__(node,tainted_vars = [self.condition])
        self._owner_candidates = None
    

    @property
    def owner_candidates(self):
        """
            如果 all_read_vars_group 中 local_vars 为空，state_vars 中有 address 或 mapping(address=>bool)，且 solidity_vars 中存在一个 msg.sender，则我们认为它可能是 owner
        """

        if self._owner_candidates is not None:
            return self._owner_candidates
        
        self._owner_candidates = []

        if len(self.all_read_vars_group.local_vars) > 0 or SolidityVariableComposed('msg.sender') not in self.all_read_vars_group.solidity_vars:
            return self._owner_candidates

        for svar in self.all_read_vars_group.state_vars:
            if svar.type == ElementaryType('address'):
                self._owner_candidates.append(svar)
            elif isinstance(svar.type, MappingType) and svar.type.type_from == ElementaryType('address') and svar.type.type_to == ElementaryType('bool'):
                self._owner_candidates.append(svar)
        return self._owner_candidates

    def __str__(self):
        return "\nRequireNode: {}\nMsg: {}\n{}".format(self.node,self.msg,self.all_read_vars_group)

def node_track(node, tainted_vars = None):
    '''
        输入一个 require node, 根据 node 找到所有依赖的变量
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
        输入一组 irs，从最后一个往上追踪

        首先从 ir.read 中找到读依赖，分别判断，如果是 Constant 或 SolidityVariable 类型，则停止查找直接存入依赖，否则继续查找，直到找不到。
        查找过程为：
            将待查变量放到待查数组中，
            由于每一行都是之前行的依赖，因此查找下一行中是否有赋值，如果有，则使用赋值替换此变量
            遇到 internalcall,则从return 开始，同样查找依赖，并更新。
    """

    if len(irs) == 0: return []

    if tainted_vars is None:
        tainted_vars = []
        tainted_ir = irs.pop()
        for r in tainted_ir.read:
            tainted_vars.append([r]) # 二维数组
    else:
        irs.pop()

    while irs:
        ir = irs.pop()
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
    irs = [ir for n in ir.function.nodes for ir in n.irs_ssa] # all_nodes()
    if len(irs) == 0: return [[]] # 由于后面使用了 sum([[]],[]),所以这里必须返回二维数组
    last_ir = irs[-1]
    if not isinstance(last_ir, Return): return [[]] # 如果最后一个 ir 不是 return，则直接返回
    return irs_ssa_track(irs) # 直接调用 irs track