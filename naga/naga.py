
from naga.core.expansions import ContractExp
from naga.core.erc import (ERC20_WRITE_FUNCS_SIG,ERC721_WRITE_FUNCS_SIG,ERC1155_WRITE_FUNCS_SIG)
from slither import Slither
class Naga():

    def __init__(self,slither:Slither,contract_address=None,contract_name = None, erc_force = None, version = None, ether = 0) -> None:
        self.slither = slither
        self.contract_name = contract_name
        self.contract_address = contract_address
        self.erc_force = erc_force
        self.version = version
        self.ether = ether
        self.entry_contracts = self._get_entry_contracts()
        
    def _get_entry_contracts(self):
        contracts = []
        if self.contract_name is not None:
            contracts =  [ContractExp(c,self.contract_address, self.erc_force, self.version, self.ether) for c in self.slither.get_contract_from_name(self.contract_name)]
        if len(contracts) == 0:
            contracts_derived = [c for c in self.slither.contracts_derived]
            contracts_called = [] # (contract,library)
            for c in contracts_derived:
                calls = [] # 获取所有的 library calls and  external high level calls
                for f in c.all_library_calls + c.all_high_level_calls:
                    calls.append(f[0])
                contracts_called += calls
            contracts = [ContractExp(c,self.contract_address,self.erc_force, self.version, self.ether) for c in list(set(contracts_derived) - set(contracts_called))]
        return contracts

    def _get_erc_contracts(self):
        
        """
            获取 ERC20,ERC721,ERC1155 的合约
        """
        self.main_contracts = []
        for c in self.slither.contracts_derived:
        #for c in list(set(contracts_derived) - set(contracts_called)):
            self.main_contracts.append(ContractExp(c))

        for c in self.main_contracts:
            funcs_sig = [ f.full_name for f in c.contract.functions_entry_points]
            if len(set(ERC20_WRITE_FUNCS_SIG) - set(funcs_sig)) == 0:
                self.erc20_contracts.append(c)
            elif len(set(ERC721_WRITE_FUNCS_SIG) - set(funcs_sig)) == 0:
                self.erc721_contracts.append(c)
            elif len(set(ERC1155_WRITE_FUNCS_SIG) - set(funcs_sig)) == 0:
                self.erc1155_contracts.append(c)

    def summary(self):
        print("\n ---- NAGA CORE SUMMARY ---- \n{}".format(list2str(self.main_contracts)))

def list2str(l):
    l = [str(i) for i in l]
    return ','.join(l)
    


