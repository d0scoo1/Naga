
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
        self._contracts_ordered = None # 排序后的合约
        self._entry_contract = None
        self.contracts_analyzed = [] # 已经分析过的合约
        self.detectors = [LimitedLiquidity,ERCMetadata,TradingParams,MissingEvent]

    @property
    def entry_contract(self):
        if self._entry_contract is not None:
            return self._entry_contract
        
        entry_contract = None
        if self.contract_name is not None:
            for co in self.contracts_ordered:
                if co.name == self.contract_name:
                    entry_contract = co
                    break

        if entry_contract == None:
            entry_contract = self.contracts_ordered[-1]

        self._entry_contract = entry_contract
        return self._entry_contract

    @property
    def contracts_ordered(self) -> List[ContractN]:
        '''
        contracts 是按依赖顺序排序的
        '''
        if self._contracts_ordered is not None:
            return self._contracts_ordered

        contracts_ordered = []
        all_contracts = list(set(self.slither.contracts) - set(self.slither.contracts_derived))
        cs_derived = [c for c in self.slither.contracts_derived]

        max_deep = len(cs_derived)
        now_deep = 0 # 防止循环依赖陷入死循环
        while cs_derived and now_deep <= max_deep:
            c = cs_derived.pop(0)
            if any(d[0] for d in c.all_high_level_calls if d[0] not in all_contracts):
                cs_derived.append(c)
            else:
                all_contracts.append(c)
                contracts_ordered.append(ContractN(c,self))
            now_deep += 1

        if len(contracts_ordered) == 0 or len(contracts_ordered) != len(self.slither.contracts_derived):
            raise Exception('#contracts_ordered: contracts_derived is not a DAG')
        
        self._contracts_ordered = contracts_ordered
        return self._contracts_ordered
    
    def analyze(self):
        for co in self.contracts_ordered:
            co.analyze()
            
    def detect_no_entry_contracts(self, erc_force=None):
        for co in self.contracts_ordered:
            if co != self.entry_contract:
                co.erc_force = erc_force
                self._detect(co)

    def detect_entry_contract(self, erc_force=None):
        self.entry_contract.erc_force = erc_force
        self._detect(self.entry_contract)

    def _detect(self,contractN:ContractN):
        if not contractN.is_analyzed:
            contractN.analyze()
        for D in self.detectors:
            d = D(self, contractN)
            d.detect()
            contractN.detectors.append(d)


