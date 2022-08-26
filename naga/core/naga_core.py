
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
        self.detectors = [LimitedLiquidity,ERCMetadata,TradingParams,MissingEvent]

    @property
    def entry_contract(self):
        if self._entry_contract is not None:
            return self._entry_contract
        
        entry_contract = None
        cs = self.slither.get_contract_from_name(self.contract_name)
        if len(cs) == 1:
            entry_contract = ContractN(cs[0],self)

        self._entry_contract = entry_contract
        return self._entry_contract

    def detect_entry_contract(self):
        self._detect(self.entry_contract)

    def _detect(self,contractN:ContractN):
        if not contractN.is_analyzed:
            contractN.analyze()
        for D in self.detectors:
            d = D(self, contractN)
            d.detect()
            contractN.detectors.append(d)


