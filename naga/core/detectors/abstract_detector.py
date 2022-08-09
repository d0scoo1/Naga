import abc
from typing import Optional, List, TYPE_CHECKING, Dict, Union, Callable


### 我们使用这一部分来管理变量的标签 ###
def _init_state_vars_label(self):
    self.exp_svars_dict = dict() # svar:StateVariable -> (label:str, rw:str)
    for svar in self.all_state_vars:
        self.exp_svars_dict[svar] = {'label': 'no_label','rw': '0000',}

def _set_state_vars_label(self,label,svars):
    for svar in svars:
        self.exp_svars_dict[svar]['label'] = label

def _get_no_label_svars(self, svars):
    no_label_svars = [svar for svar in self.exp_svars_dict if self.exp_svars_dict[svar]['label'] == 'no_label']
    return [svar for svar in svars if svar in no_label_svars]

def _get_label_svars(self, label):
    return [svar for svar in self.exp_svars_dict if self.exp_svars_dict[svar]['label'] == label]

class AbstractDetector(metaclass=abc.ABCMeta):

    def __init__(
        self, naga:"Naga"
    ):
        
        self.naga: "Naga" = naga

    @abc.abstractmethod
    def _detect(self):
        """TODO Documentation"""

    # pylint: disable=too-many-branches
    def detect(self):
        self._detect()

    @abc.abstractmethod
    def summary(self) -> Dict[str, Union[str, List[str]]]:
        """TODO Documentation"""
