
'''
Naga core 将装载和分析 ContractN 和 ContractN 内部的函数
'''
from slither import Slither
from typing import Optional, List, TYPE_CHECKING, Dict, Union, Callable
from .contract_naga import ContractN

from naga.detectors import LimitedLiquidity,ERCMetadata,TradingParams,MissingEvent

class NagaCore():

    def __init__(self, slither:Slither, contract_name = None) -> None:
        self.slither = slither
        self.contract_name = contract_name
        self._entry_contract = None
        self.contracts_analyzed = [] # 已经分析过的合约

    @property
    def entry_contract(self):
        if self._entry_contract is not None:
            return self._entry_contract
        
        entry_contract = None
        cs = self.slither.get_contract_from_name(self.contract_name)
        if len(cs) == 1:
            entry_contract = ContractN(cs[0],self)
        elif len(self.entry_contracts) == 1:
            entry_contract = ContractN(self.entry_contracts[0],self)

        self._entry_contract = entry_contract
        return self._entry_contract
    @property
    def entry_contracts(self):
        contracts_derived  = self.slither.contracts_derived 
        called_contracts = []
        for c in contracts_derived:
            called_contracts += [d[0] for d in c.all_high_level_calls + c.all_library_calls]

        return list(set(contracts_derived)-set(called_contracts))

    def detect(self,contractN,erc_force = None,detectors:List[Callable] = [LimitedLiquidity,ERCMetadata,TradingParams,MissingEvent]):
        if not contractN.is_analyzed:
            contractN.analyze()
        contractN.erc_force = erc_force
        for D in detectors:
            d = D(self, contractN)
            d.detect()
            contractN.detectors.append(d)

    def detect_all_entry_contracts(self,erc_force = None):
        for c in self.entry_contracts:
            c.erc_force = erc_force
            self._oo_detect(c)

    def detect_entry_contract(self,erc_force = None):
        self.entry_contract.erc_force = erc_force
        self._oo_detect(self.entry_contract)

    def _oo_detect(self,contractN:ContractN):
        if not contractN.is_analyzed:
            contractN.analyze()
        if contractN.is_erc:
            for D in [LimitedLiquidity,ERCMetadata,TradingParams,MissingEvent]:
                d = D(self, contractN)
                d.detect()
                contractN.detectors.append(d)
        else:
            d = MissingEvent(self, contractN) # 否则直接调用最 Missing event
            d.detect()
            contractN.detectors.append(d)
    


