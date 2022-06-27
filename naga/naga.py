
from naga.core.expansions import ContractExp
from naga.core.erc import (ERC20_WRITE_FUNCS_SIG,ERC721_WRITE_FUNCS_SIG,ERC1155_WRITE_FUNCS_SIG)

class Naga():
    def __init__(self, slither) -> None:
        self.slither = slither
        self.main_contracts = []
        self.erc20_contracts = []
        self.erc721_contracts = []
        self.erc777_contracts = []
        self.erc1155_contracts = []

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
        self.main_contracts =  list(set(contracts_derived) - set(contracts_called))
        for c in self.main_contracts:
            funcs_sig = [ f.full_name for f in c.functions_entry_points]
            if len(set(ERC20_WRITE_FUNCS_SIG) - set(funcs_sig)) == 0:
                self.erc20_contracts.append(ContractExp(c))
            elif len(set(ERC721_WRITE_FUNCS_SIG) - set(funcs_sig)) == 0:
                self.erc721_contracts.append(ContractExp(c))
            elif len(set(ERC1155_WRITE_FUNCS_SIG) - set(funcs_sig)) == 0:
                self.erc1155_contracts.append(ContractExp(c))
    
    def summary(self):
        print("\n ---- NAGA CORE SUMMARY ---- \nERC20:{}\nERC721:{}\nERC1155:{}".format(list2str(self.erc20_contracts),list2str(self.erc721_contracts),list2str(self.erc1155_contracts)))


def list2str(l):
    l = [str(i) for i in l]
    return ','.join(l)
    


