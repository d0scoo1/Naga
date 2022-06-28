import abc

from typing import List, Dict,Optional
from slither.core.declarations import Contract
from slither.core.variables.state_variable import StateVariable
from slither.core.solidity_types.mapping_type import MappingType
from naga.core.expansions import ContractExp

from naga.core.expansions.state_variable_exp import (StateVarType,StateVariableExp)
from naga.core.erc import (ERC20_WRITE_FUNCS_SIG,ERC721_WRITE_FUNCS_SIG,ERC1155_WRITE_FUNCS_SIG)

class AbstractDetector(metaclass=abc.ABCMeta):
    def __init__(self,contractExp:ContractExp) -> None:
        self.contractExp = contractExp

    @abc.abstractmethod
    def _detect(self):
        pass

    def detect(self):
        self._detect()

    @abc.abstractmethod
    def result_dict(self):
        return dict()