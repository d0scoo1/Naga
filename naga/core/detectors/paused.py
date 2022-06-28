from .abstract_detector import AbstractDetector
from typing import List, Dict,Optional
class Paused(AbstractDetector):

    def _detect(self):
        print('paused')
    
    def result_dict(self):
        return {}