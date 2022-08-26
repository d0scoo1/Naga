from typing import List, Dict,Optional
from slither.core.variables.state_variable import StateVariable
from .abstract_detector import *

def detect_trading_params(self):
    '''
    交易费一般是 uint 类型，这些变量 user 只读，出现在ERC写函数中
    '''
    # self.token_written_functions
    # 用户只读变量中，无 label 的 int 变量
    candidates = [svar for svar in self.get_svars_by_label() if str(svar.type).startswith('uint')]

    trading_params = []
    # 检查变量是否出现在交易函数中
    for svar in candidates:
        # 如果变量出现在交易函数中，则认为是交易参数
        if len(set(self.state_var_read_functions_dict[svar]) & set(self.token_written_functions))> 0:
            trading_params.append(svar)
    
    for svar in trading_params:
        self.update_svarn_label(svar,VarLabel.param,DType.PARAMETERS,DMethod.DEPENDENCY)

    # mutable_params
    for svar in trading_params:
        if svar in self.state_vars_user_only_read_owner_updated:
            self.update_svarn_label(svar,VarLabel.param,DType.MUTABLE_PARAMETERS,DMethod.DEPENDENCY)


class TradingParams(AbstractDetector):
    def _detect(self):
        detect_trading_params(self.cn)
    
    def summary(self):
        return {"MP":{}}