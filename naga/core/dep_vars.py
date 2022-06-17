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


class DepVars:
    '''
        一个 node 可能依赖一组变量，我们使用这个类来管理这些变量
    '''
    def __init__(self, dep_vars = None,dep_irs_ssa = None):
        self.dep_vars = dep_vars
        self.dep_irs_ssa = dep_irs_ssa
        self.state_vars = []
        self.local_vars = []
        self.solidity_vars = []
        self.constant_vars = []
        self.other_vars = []
        self.__divide_vars()
    
    def __divide_vars(self):
        if self.dep_vars is None and self.dep_irs_ssa is None:
            return

        if self.dep_irs_ssa is not None:
            self.dep_vars = []
            var_hashable = set()
            var_unhashable = []
            for v in self.dep_irs_ssa:
                if isinstance(v,(StateIRVariable,LocalIRVariable)):
                    var_hashable.add(v._non_ssa_version)
                else: 
                    var_unhashable.append(v)
            self.dep_vars = list(var_hashable) + var_unhashable
        
        for v in self.dep_vars:
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

    def __str__(self):
        return "State Vars:[{}] Local Vars:[{}] Solidity Vars:[{}] Constant:[{}]\n".format(list2str(self.state_vars),list2str(self.local_vars),list2str(self.solidity_vars),list2str(self.constant_vars))

def list2str(l):
    l = [str(i) for i in l]
    return ','.join(l)