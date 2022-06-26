
from enum import Enum
class VarTypeEXT(Enum):
    UNKNOWN = 0
    OWNER = 1
    BWLIST = 2
    PAUSED = 3

class VariableEXT():
    """
        这个类用于扩展追踪的 var (主要是 state), 以方便的查询变量相关的 读、写、require
    """
    def __init__(self,var):
        self.var = var
        self.functions_written = None # 这里的 function 都是 public / external
        self.functions_read = None
        self.functions_read_in_requires = None
        #self.requires:List[RequireExp] = None
        #self.exp_var_type:VarExpType = VarExpType.UNKNOWN

