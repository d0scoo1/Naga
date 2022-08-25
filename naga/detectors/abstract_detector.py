import abc
from typing import Optional, List, TYPE_CHECKING, Dict, Union, Callable
from enum import Enum

class VarLabel(Enum):
    # AC
    owner = 'owner'
    role = 'role'
    # LL
    paused = 'paused'
    blacklist = 'blacklist'
    # VS
    _totalSupply = 'totalSupply'
    # MM
    _name = 'name'
    _symbol = 'symbol'
    _decimals = 'decimals'
    _uri = 'uri'
    # ME
    param = 'param'

    _balances = 'balances'
    _allowances = 'allowances'
    _owners = 'owners'
    _tokenApprovals = 'tokenApprovals'
    _operatorApprovals = 'operatorApprovals'

    def __str__(self):
        return self.value

class DType(Enum): # detection type
    ACCESS_CONTROL = 'AC'
    LIMITED_LIQUIDITY = 'LL'
    VULNERABLE_SCARCITY = 'VS'
    MUTABLE_METADATA = 'MM'
    MUTABLE_PARAMETERS = 'MP'
    MISSING_EVENTS = 'ME'

    METADATA = 'metadata'
    PARAMETERS = 'parameters'
    ASSET = 'asset'

    def __str__(self):
        return self.value

class DMethod(Enum): # detection method
    INHERITANCE = 'i'
    MODIFIER = 'm'
    GETTER = 'g'
    NAME = 'n'
    DEPENDENCY = 'd'

    def __str__(self):
        return self.value

class StateVarExp():
    def __init__(self,svar, label = None, dType = None,external = False,callers = []):
        self.svar = svar
        self.name = svar.canonical_name
        self.label:VarLabel = label
        self.rw = '0000'
        self.dType:DType = dType
        self.dMethods:DMethod = {
            DMethod.INHERITANCE: False, # inheritance
            DMethod.MODIFIER: False, # modifier
            DMethod.GETTER: False, # getter
            DMethod.NAME: False, # name
            DMethod.DEPENDENCY: False  # dependency
        }
        self.external = external # 是否为 address 调用的外部变量
        self.callers = callers # 外部调用者
    
    def __str__(self):
        return '{}: {}, {}, {}, \t{}'.format(self.name,self.label,self.rw,self.dType,':'.join(['{}:{}'.format(k,v) for k,v in self.dMethods.items()]))

    def toJson(self):
        return {
            'name':self.name,
            'type':str(self.svar.type),
            'label':str(self.label),
            'rw':self.rw,
            'dType':str(self.dType),
            'dMethods':{ k.value:v for k,v in self.dMethods.items()},
            'external':self.external,
        }

### 我们使用这一部分来管理变量的标签 ###

def _set_state_vars_label(self,svars, label:VarLabel,dType:DType,dMethod:DMethod,caller_dict = {}):
    for svar in svars:
        if svar not in self.exp_svars_dict:
            #print('[WARNING] {} not in exp_svars_dict'.format(svar))
            self.exp_svars_dict[svar] = StateVarExp(svar,external = True, callers = caller_dict[svar])
        self.exp_svars_dict[svar].label = label
        self.exp_svars_dict[svar].dType = dType
        if dMethod != None:
            self.exp_svars_dict[svar].dMethods[dMethod] = True

def _get_no_label_svars(self,):
    return [svar for svar in self.exp_svars_dict if self.exp_svars_dict[svar].label == None]

def _get_label_svars(self, label):
    return [svar for svar in self.exp_svars_dict if self.exp_svars_dict[svar].label == label]

def _get_dtype_svars(self, dtype):
    return [svar for svar in self.exp_svars_dict if self.exp_svars_dict[svar].dType == dtype]

class AbstractDetector(metaclass=abc.ABCMeta):

    def __init__(
        self, cexp
    ):
        
        self.cexp = cexp

    @abc.abstractmethod
    def _detect(self):
        """TODO Documentation"""

    # pylint: disable=too-many-branches
    def detect(self):
        self._detect()

    @abc.abstractmethod
    def output(self) -> Dict[str, Union[str, List[str]]]:
        """TODO Documentation"""
