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
    ALLOWANCES = 6 
    NAME = 7
    SYMBOL = 8
    DECIMALS = 9
    OWNER_OF = 10
    TOKEN_APPROVALS = 11
    OPERATOR_APPROVALS = 12
    URL = 13
    UNFAIR_SETTING = 14

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
        if self == StateVarType.ALLOWANCES:
            return "ALLOWANCES"
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
        self.is_user_read = False
        self.is_user_write = False
        self.is_owner_read = False
        self.is_owner_write = False
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
            if rf in self.contract_exp.owner_in_require_functions:
                self.functions_owner_read.append(rf)
            else:
                self.functions_user_read.append(rf)

        for wf in self.contract_exp.state_var_written_functions_dict[self.state_variable]:
            if wf.function.is_constructor: continue
            if wf in self.contract_exp.owner_in_require_functions:
                self.functions_owner_written.append(wf)
            else:
                self.functions_user_written.append(wf)

        self.is_user_read = len(self.functions_user_read) > 0
        self.is_user_write = len(self.functions_user_written) > 0
        self.is_owner_read = len(self.functions_owner_read) > 0
        self.is_owner_write = len(self.functions_owner_written) > 0

    def __str__(self) -> str:
        return self.state_variable.name

    def summary(self) -> str:
        return 'State Variable:{:^20}, Type:{:^12}, User:R:{:^3},W:{:^3}, Owner:R:{:^3},W:{:^3}'.format(self.state_variable.name[:20],self.stype,self.is_user_read,self.is_user_write,self.is_owner_read,self.is_owner_write)




