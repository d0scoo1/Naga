
from .core.contract_ext import ContractEXT
from .core.erc import (ERC20_WRITE_FUNCS_SIG,ERC721_WRITE_FUNCS_SIG,ERC1155_WRITE_FUNCS_SIG)

class Naga():
    def __init__(self, slither) -> None:
        self.slither = slither

        self.contracts_erc20 = []
        self.contracts_erc721 = []
        self.contracts_erc777 = []
        self.contracts_erc1155 = []

        self._get_erc_contracts()

    def _get_erc_contracts(self):
        contracts_derived = [c for c in self.slither.contracts_derived]
        contracts_called = [] # (contract,library)
        for c in contracts_derived:
            calls = [] # 获取所有的 library calls and  external high level calls
            for f in c.all_library_calls + c.all_high_level_calls:
                calls.append(f[0])
            contracts_called += calls
        
        """
            获取 ERC20,ERC721,ERC1155 的合约
        """
        for c in list(set(contracts_derived) - set(contracts_called)):
            funcs_sig = [ f.full_name for f in c.functions_entry_points]
            if len(set(ERC20_WRITE_FUNCS_SIG) - set(funcs_sig)) == 0:
                self.contracts_erc20.append(ContractEXT(c))
            elif len(set(ERC721_WRITE_FUNCS_SIG) - set(funcs_sig)) == 0:
                self.contracts_erc721.append(ContractEXT(c))
            elif len(set(ERC1155_WRITE_FUNCS_SIG) - set(funcs_sig)) == 0:
                self.contracts_erc1155.append(ContractEXT(c))
    
    def summary(self):
        print("\n ---- NAGA CORE SUMMARY ---- \nERC20:{}\nERC721:{}\nERC1155:{}".format(list2str(self.contracts_erc20),list2str(self.contracts_erc721),list2str(self.contracts_erc1155)))


def list2str(l):
    l = [str(i) for i in l]
    return ','.join(l)
    


