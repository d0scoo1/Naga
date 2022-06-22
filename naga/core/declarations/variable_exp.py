
from typing import Dict, TYPE_CHECKING, List, Optional, Set, Union, Callable, Tuple
from slither.core.cfg.node import Node, NodeType

from .function_exp import FunctionExp
from .require_exp import RequireExp

from enum import Enum
class VarExpType(Enum):
    UNKNOWN = 0
    OWNER = 1
    BWLIST = 2
    PAUSED = 3

class VariableExp():
    """
        这个类用于扩展追踪的 var (主要是 state), 以方便的查询变量相关的 读、写、require
    """
    def __init__(self,var):
        self.var = var
        self.functions_written:List[FunctionExp] = None # 这里的 function 都是 public / external
        self.functions_read:List[FunctionExp] = None
        self.functions_read_in_requires:List[FunctionExp] = None
        #self.requires:List[RequireExp] = None
        #self.exp_var_type:VarExpType = VarExpType.UNKNOWN

