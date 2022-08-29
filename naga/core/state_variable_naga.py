
from typing import Optional, List, TYPE_CHECKING, Dict, Union, Callable
from enum import Enum
from unittest.mock import DEFAULT

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
    TOTALSUPPLY = 'totalSupply'

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

class StateVarN():
    def __init__(self,svar, label = None, dType = None,external = False,callers = []):
        self.svar = svar
        self.name = svar.name
        self.canonical_name = svar.canonical_name
        self.label:VarLabel = label
        self.rw = [0,0,0,0]
        self.dType:DType = dType
        self.dMethods:DMethod = {
            DMethod.INHERITANCE: False, # inheritance
            DMethod.MODIFIER: False, # modifier
            DMethod.GETTER: False, # getter
            DMethod.NAME: False, # name
            DMethod.DEPENDENCY: False  # dependency
        }
        self.external = external # 是否为 address 调用的外部变量
        self.callers = callers # 调用者
    
    @property
    def rw_str(self):
        return ''.join(str(i) for i in self.rw)

    def __str__(self):
        return '{}, {}: {}, {}, {}, \t{}'.format(self.external, self.name,self.label,self.rw,self.dType,':'.join(['{}:{}'.format(k,v) for k,v in self.dMethods.items()]))

    def toJson(self):
        return {
            'name':self.name,
            'type':str(self.svar.type),
            'label':str(self.label),
            'rw':self.rw_str,
            'dType':str(self.dType),
            'dMethods':{ k.value:v for k,v in self.dMethods.items()},
            'external':self.external,
        }

