from slither.core.variables.state_variable import StateVariable
from typing import List, Dict, Tuple

from .require_exp import RequireExp
from .function_exp import FunctionExp
from enum import Enum
class StateVarType(Enum):
    UNKNOWN = 0
    OWNER = 1
    BWLIST = 2
    PAUSED = 3
    TOTAL_SUPPLY = 4
    BALANCES = 5
    ALLOWED = 6
    IDENTIFY = 7
    UNFAIR_SETTING = 8

    def __str__(self):
        if self == StateVarType.UNKNOWN:
            return "UNKNOWN"
        if self == StateVarType.OWNER:
            return "OWNER"
        if self == StateVarType.BWLIST:
            return "BWLIST"
        if self == StateVarType.PAUSED:
            return "PAUSED"
        if self == StateVarType.TOTAL_SUPPLY:
            return "TOTAL_SUPPLY"
        if self == StateVarType.BALANCES:
            return "BALANCES"
        if self == StateVarType.ALLOWED:
            return "ALLOWED"
        if self == StateVarType.IDENTIFY:
            return "IDENTIFY"
        if self == StateVarType.UNFAIR_SETTING:
            return "UNFAIR_SETTING"
        return "Unknown type"

class StateVariableExp():
    """
        一个 state variable 包括以下几个部分:
        1. 它是否可以被用户读写，是否可以被 owner 读写（不包括 constructor）
        2. 它被标记的类型，是 owner，bwlist，paused，还是其他
    """
    def __init__(self,svar:StateVariable,contract_exp,stype:StateVarType = StateVarType.UNKNOWN):
        self.state_variable:StateVariable = svar
        self.contract_exp = contract_exp
        self.stype = stype
        self.is_user_readable = False
        self.is_user_writable = False
        self.is_owner_readable = False
        self.is_owner_writable = False
        self.functions_user_read: List["FunctionExp"] = []
        self.functions_user_written: List["FunctionExp"] = []
        self.functions_owner_read: List["FunctionExp"] = []
        self.functions_owner_written: List["FunctionExp"] = []
        self.read_in_require_functions: List["FunctionExp"]= []
        self.read_in_requires: List["RequireExp"] = []

        self.__update_functions()
    
    def __update_functions(self):
        self.read_in_require_functions = self.contract_exp.state_var_read_in_require_functions_dict[self.state_variable]
        self.read_in_requires = self.contract_exp.state_var_read_in_requires_dict[self.state_variable]
        self.functions_user_read = []
        self.functions_owner_read = []
        self.functions_user_written = []
        self.functions_owner_written = []
        for rf in self.contract_exp.state_var_read_functions_dict[self.state_variable]:
            if rf.function.is_constructor: continue
            if len(rf.owners) == 0:
                self.functions_user_read.append(rf)
            else:
                self.functions_owner_read.append(rf)

        for wf in self.contract_exp.state_var_written_functions_dict[self.state_variable]:
            if wf.function.is_constructor: continue
            if len(wf.owners) == 0:
                self.functions_user_written.append(wf)
            else:
                self.functions_owner_written.append(wf)

        self.is_user_readable = len(self.functions_user_read) > 0
        self.is_user_writable = len(self.functions_user_written) > 0
        self.is_owner_readable = len(self.functions_owner_read) > 0
        self.is_owner_writable = len(self.functions_owner_written) > 0

    """
    def set_data(self, read_functions: List["FunctionExp"], write_functions: List["FunctionExp"],read_in_require_functions:List["FunctionExp"],read_in_requires:List["RequireExp"]):
        self.read_in_require_functions = read_in_require_functions
        self.read_in_requires = read_in_requires
        self.functions_user_read = []
        self.functions_owner_read = []
        self.functions_user_written = []
        self.functions_owner_written = []
        for rf in read_functions:
            if rf.function.is_constructor: continue
            if len(rf.owners) == 0:
                self.functions_user_read.append(rf)
            else:
                self.functions_owner_read.append(rf)

        for wf in write_functions:
            if wf.function.is_constructor: continue
            if len(wf.owners) == 0:
                self.functions_user_written.append(wf)
            else:
                self.functions_owner_written.append(wf)

        self.is_user_readable = len(self.functions_user_read) > 0
        self.is_user_writable = len(self.functions_user_written) > 0
        self.is_owner_readable = len(self.functions_owner_read) > 0
        self.is_owner_writable = len(self.functions_owner_written) > 0
    """
    def __str__(self) -> str:
        return self.state_variable.name

    def summary(self) -> str:
        return 'State Variable:{:^20}, Type:{:^12}, User:R:{:^3},W:{:^3}, Owner:R:{:^3},W:{:^3}'.format(self.state_variable.name[:20],self.stype,self.is_user_readable,self.is_user_writable,self.is_owner_readable,self.is_owner_writable)




