from .abstract_detector import *
from slither.core.solidity_types.elementary_type import ElementaryType

def detect_paused(self):
    """
    Before Functions: detect_owners_bwList
    搜索所有的 paused
    paused 符合以下特点，出现在 tranfer 的 condition 中（没有 local variables 出现在 condition 中），bool 类型，只有 owner 可以修改
    """
    paused_candidates = [
        svar
        for svar in self.state_vars_user_only_read_owner_updated
        if svar.type == ElementaryType('bool')
    ]

    paused = []
    for svar in list(set(paused_candidates)):
        funcs_sigs = [f.function.full_name for f in self.state_var_read_in_condition_functions_dict[svar]]
        if len(set(funcs_sigs) & set(self.token_write_function_sigs)) > 0: # 如果变量 condition function 出现在 token 写函数中
            paused.append(svar)
    for p in paused:
        self.update_svarn_label(p,VarLabel.paused,DType.LIMITED_LIQUIDITY,DMethod.DEPENDENCY)

class LimitedLiquidity(AbstractDetector):
    def _detect(self):
        detect_paused(self.cn)

    def summary(self):
        return {'LL':{}}