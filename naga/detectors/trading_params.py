from typing import List, Dict,Optional
from slither.core.variables.state_variable import StateVariable
from .abstract_detector import (AbstractDetector, VarLabel, DType, DMethod,_set_state_vars_label,_get_no_label_svars,_get_label_svars, _get_dtype_svars)

def detect_trading_params(self):
    '''
    交易费一般是 uint 类型，这些变量 user 只读，出现在ERC写函数中
    '''
    # self.token_written_functions
    # 用户只读变量中，无 label 的 int 变量
    candidates = [svar for svar in _get_no_label_svars(self) if str(svar.type).startswith('uint')]

    trading_params = []
    # 检查变量是否出现在交易函数中
    for svar in candidates:
        # 如果变量出现在交易函数中，则认为是交易参数
        if len(set(self.state_var_read_functions_dict[svar]) & set(self.token_written_functions))> 0:
            trading_params.append(svar)
    _set_state_vars_label(self,trading_params,VarLabel.param,DType.PARAMETERS,DMethod.DEPENDENCY)

    mutable_params = []
    for svar in trading_params:
        if svar in self.state_vars_user_only_read_owner_updated:
            mutable_params.append(svar)
    _set_state_vars_label(self,mutable_params,VarLabel.param,DType.MUTABLE_PARAMETERS,DMethod.DEPENDENCY)


class TradingParams(AbstractDetector):
    def _detect(self):
        detect_trading_params(self.cexp)
    def summary(self):
        return {}