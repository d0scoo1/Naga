from .abstract_detector import AbstractDetector
from typing import List, Dict,Optional

class LackEvents(AbstractDetector):

    def _detect(self):
        print('lack_events')
    
    def result_dict(self):
        return {}