from .abstract_detector import *

def detect_missing_event_functions(self):
    """
    Before Functions: detect_owners_bwList
    如果一个 function 写了 state variable，则应当发送一个 event，提醒用户，这里寻找缺少的 event 的 function。
    我们并不考虑 event 的参数，关于 event 和实际操作不一致的问题：TokenScope: Automatically Detecting Inconsistent Behaviors of Cryptocurrency Tokens in Ethereum
    """

    lack_event_owner_functions = []
    lack_event_user_functions = []
    for f in self.state_var_written_functions:
        if not f.is_constructor_or_initializer and len(f.events) == 0:
            if f in self.owner_in_condition_functions:
                lack_event_owner_functions.append(f)
            else:
                lack_event_user_functions.append(f)
    
    self.lack_event_functions = lack_event_owner_functions + lack_event_user_functions
    self.lack_event_owner_functions = lack_event_owner_functions
    self.lack_event_user_functions = lack_event_user_functions

class MissingEvent(AbstractDetector):
    def _detect(self):
        detect_missing_event_functions(self.cn)

    def summary(self):
        self = self.cn
        summary ={
        'LE_functions': [],
        'LE_user_svars':{},
        'LE_owner_svars':{},
        'LE_rw':{
            '0000':[],'0001':[], '0010':[],'0011':[], '0100':[],'0101':[], '0110':[],'0111':[],'1000':[],'1001':[], '1010':[],'1011':[], '1100':[],'1101':[], '1110':[],'1111':[],}
        }

        for f in self.lack_event_functions:
            summary['LE_functions'].append(f.function.name)

        lack_event_user_erc_svars = dict() # 查找用户是写了什么变量
        lack_event_owner_erc_svars = dict() # 检查 owner 写了什么变量没有提示
        
        for dt in DType:
            lack_event_user_erc_svars[dt.value] = []
            lack_event_owner_erc_svars[dt.value] = []
        lack_event_user_erc_svars['None'] = []
        lack_event_owner_erc_svars['None'] = []
        for f in self.lack_event_user_functions:
            for svar in f.function.all_state_variables_written():
                exp_svar = self.svarn_pool[svar]
                if exp_svar.dType != None:
                    lack_event_user_erc_svars[exp_svar.dType.value].append({"function":f.function.full_name, "svar":svar.name})
                else:
                    lack_event_user_erc_svars['None'].append({"function":f.function.full_name, "svar":svar.name})
        for f in self.lack_event_owner_functions:
            for svar in f.function.all_state_variables_written():
                exp_svar = self.svarn_pool[svar]
                if exp_svar.dType != None:
                    lack_event_owner_erc_svars[exp_svar.dType.value].append({"function":f.function.full_name, "svar":svar.name})
                else:
                    lack_event_owner_erc_svars['None'].append({"function":f.function.full_name, "svar":svar.name})
        
        summary['LE_user_svars'] = lack_event_user_erc_svars
        summary['LE_owner_svars'] = lack_event_owner_erc_svars

        for f in self.lack_event_functions:
            for svar in f.function.all_state_variables_written():
                summary['LE_rw'][self.svarn_pool[svar].rw_str].append({"function":f.function.full_name, "svar":svar.name})

        return {'ME':summary}