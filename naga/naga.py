from slither import Slither

from .core.naga_core import NagaCore
class Naga(NagaCore):
    def __init__(self, slither:Slither, contract_name = None) -> None:
        super().__init__(slither, contract_name)
