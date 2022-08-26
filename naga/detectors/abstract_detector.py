import abc
from typing import Optional, List, TYPE_CHECKING, Dict, Union, Callable
from naga.core.state_variable_naga import VarLabel, DType, DMethod, StateVarN


class AbstractDetector(metaclass=abc.ABCMeta):

    def __init__(self, naga, cn,) -> None:
        '''
        naga: 传递 naga 对象，因为有可能需要查询其他的 contract
        cn: 传递当前 contract 对象
        '''
        self.naga = naga
        self.cn = cn

    @abc.abstractmethod
    def _detect(self):
        """TODO Documentation"""

    # pylint: disable=too-many-branches
    def detect(self):
        self._detect()

    @abc.abstractmethod
    def summary(self) -> Dict[str, Union[str, List[str]]]:
        """TODO Documentation"""
