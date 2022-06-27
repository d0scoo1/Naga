import abc

from naga import Naga
from naga.core.expansions import ContractExp
class AbstractDetector(metaclass=abc.ABCMeta):
    def __init__(self,naga:Naga) -> None:
        self.naga = Naga

        """
            检测 
        """