from xmlrpc.client import Boolean
from slither.core.variables.state_variable import StateVariable
from typing import List, Dict, Tuple
from .require_ext import RequireEXT
from .function_ext import FunctionEXT
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
    PARAMETER = 8

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
        if self == StateVarType.PARAMETER:
            return "PARAMETER"
        return "Unknown type"

class StateVariableEXT():
    """
        一个 state variable 包括以下几个部分:
        1. 它是否可以被用户读写，是否可以被 owner 读写（不包括 constructor）
        2. 它被标记的类型，是 owner，bwlist，paused，还是其他
    """
    def __init__(self,svar:StateVariable):
        self.svar:StateVariable = svar
        self.stype = StateVarType.UNKNOWN
        self.is_user_readable:Boolean = False
        self.is_user_writable:Boolean = False
        self.is_owner_readable:Boolean = False
        self.is_owner_writable:Boolean = False
        self.functions_user_read: List["FunctionEXT"] = []
        self.functions_user_written: List["FunctionEXT"] = []
        self.functions_owner_read: List["FunctionEXT"] = []
        self.functions_owner_written: List["FunctionEXT"] = []
        self.read_in_require_functions: List["FunctionEXT"]= []
        self.read_in_requires: List["RequireEXT"] = []

    def set_data(self, read_functions: List["FunctionEXT"], write_functions: List["FunctionEXT"],read_in_require_functions:List["FunctionEXT"],read_in_requires:List["RequireEXT"]):
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

    def __str__(self) -> str:
        return self.svar.name

    def summary(self) -> str:
        return 'State Variable:{:^20}, Type:{:^12}, User:R:{:^3},W:{:^3}, Owner:R:{:^3},W:{:^3}'.format(self.svar.name[:20],self.stype,self.is_user_readable,self.is_user_writable,self.is_owner_readable,self.is_owner_writable)




