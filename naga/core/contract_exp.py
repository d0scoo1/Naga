from slither.core.declarations import Contract

from naga.utils.token import(
    IERC20_FUNCTIONS_SIG,
    IERC721_FUNCTIONS_SIG,
    IERC777_FUNCTIONS_SIG,
    IERC1155_FUNCTIONS_SIG,
)
from .function_exp import FunctionExp

class ContractExp():
    def __init__(self,contract: Contract):
        self.contract = contract
        self._function_exps = None

    def _init(self):
        self.function_exps = []
        for func in self.contract.functions_entry_points():
            self.function_exps.append(FunctionExp(func))

    def owners(self):
        """
        :return: list of owners
        """
        return []

    def functions_ownable(self):
        """
        :return: list of functions that only can be called by owners
        """
        return []

    def get_owners_by_function_name(self,function_name):
        return []
    
    def get_functions_by_owner(self,owner):
        return []
