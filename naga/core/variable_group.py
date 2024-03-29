from typing import List
from slither.core.declarations import (
    SolidityVariable,
    SolidityVariableComposed,
    SolidityFunction,
)

from slither.slithir.variables import (
    Constant,
    LocalIRVariable,
    ReferenceVariable,
    StateIRVariable,
    TemporaryVariable,
    TupleVariable,
)
from slither.core.variables.state_variable import StateVariable
from slither.core.variables.local_variable import LocalVariable


class VariableGroup():
    '''
    一个 node 可能依赖一组变量，我们使用这个类来管理这些变量
    '''
    def __init__(self, all_vars = None,dep_irs_ssa = None, callers = {},params2agrs = {}):
        super().__init__()
        self.all_vars = all_vars
        self.dep_irs_ssa = dep_irs_ssa
        self.state_vars:List[StateVariable] = []
        self.local_vars = []
        self.solidity_vars = []
        self.constant_vars = []
        self.other_vars = []
        self.callers = callers # 依赖的变量可能是由 High Level 函数产生的，这里保存调用者信息
        self.params2agrs = params2agrs # 参数到参数的映射
        self.__divide_vars()

    def __divide_vars(self):
        if self.all_vars is None and self.dep_irs_ssa is None:
            return

        if self.dep_irs_ssa is not None:
            self.all_vars = []
            var_hashable = set()
            var_unhashable = []
            for v in self.dep_irs_ssa:
                
                if isinstance(v,(StateIRVariable,LocalIRVariable)):
                    var_hashable.add(v._non_ssa_version)
                else: 
                    var_unhashable.append(v)
            self.all_vars = list(var_hashable) + var_unhashable

        for i in range(len(self.all_vars)):
            v = self.all_vars[i]
            if isinstance(v,LocalVariable) and v in self.params2agrs:
                self.all_vars[i] = self.params2agrs[v]
 
        for v in self.all_vars:
            if isinstance(v,StateVariable):
                self.state_vars.append(v)
            elif isinstance(v,LocalVariable):
                self.local_vars.append(v)
            elif isinstance(v,SolidityVariable):
                self.solidity_vars.append(v)
            elif isinstance(v,Constant):
                self.constant_vars.append(v)
            else:
                self.other_vars.append(v)

    def _dict(self):
        return {
            "state_vars":[str(s) for s in self.state_vars],
            "local_vars":[str(s) for s in self.local_vars],
            "solidity_vars":[str(s) for s in self.solidity_vars],
            "constant_vars":[str(s) for s in self.constant_vars],
            "other_vars":[str(s) for s in self.other_vars],
        }

    def __str__(self):
        return "State Vars:[{}] Local Vars:[{}] Solidity Vars:[{}] Constant:[{}]".format(list2str(self.state_vars),list2str(self.local_vars),list2str(self.solidity_vars),list2str(self.constant_vars))

def var_group_combine(varGroups):
    vg = VariableGroup()

    all_callers = {}
    for t in varGroups:
        vg.state_vars += [v for v in t.state_vars if v not in vg.state_vars]
        vg.local_vars += [v for v in t.local_vars if v not in vg.local_vars]
        vg.solidity_vars += [v for v in t.solidity_vars if v not in vg.solidity_vars]
        vg.constant_vars += [v for v in t.constant_vars if v not in vg.constant_vars]
        vg.other_vars += [v for v in t.other_vars if v not in vg.other_vars]
        
        for caller in t.callers:
            if caller not in all_callers:
                all_callers[caller] = []
            all_callers[caller] += t.callers[caller]

    vg.all_vars = vg.state_vars + vg.local_vars + vg.solidity_vars + vg.constant_vars + vg.other_vars

    for caller in all_callers:
        all_callers[caller] = list(set(all_callers[caller]))
    vg.callers = all_callers 
    return vg

def list2str(l):
    l = [str(i) for i in l]
    return ','.join(l)

    