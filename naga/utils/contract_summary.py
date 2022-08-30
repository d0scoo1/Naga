
from naga.core.state_variable_naga import DType, VarLabel, StateVarN, DMethod

def state_variables(self):
    summary = {
        'svars': [],
        'svars_detection': {},
        'svars_label': {},
        'multistage_owners': [],
        'state_variables_label_rw': {},
        #'state_variables_rw': {},
    }

    for svar in self.svarn_pool.values(): 
        summary['svars'].append(svar.toJson())

    for dt in DType: 
        summary['svars_detection'][dt.value] = [svar.name for svar in self.get_svars_by_dtype(dt)]
    for label in VarLabel: 
        summary['svars_label'][label.value] = [svar.name for svar in self.get_svars_by_label(label)]

    summary['multistage_owners'] = [svar.name for svar in self.multistage_owners]

    return summary

def modifiers(self):
    summary = {'all_modifiers':[]}
    for m in self.contract.modifiers:
        modifier = {
            'name': m.name,
            'state_variables_read':[svar.name for svar in m.all_state_variables_read()],
            'state_variables_written': [svar.name for svar in m.all_state_variables_written()],
            'solidity_variables_read':[svar.name for svar in m.all_solidity_variables_read()],
        }
        summary['all_modifiers'].append(modifier)

    return summary

def functions(self):
    summary = {'functions':[]}
    for f in self.functions:
        f_summary = {
            'name': f.function.full_name,
            'owner_in_condition': f in self.owner_in_condition_functions,
            #'parameters':f.function.parameters,
            'state_variables_read':[svar.name for svar in f.function.all_state_variables_read()],
            'state_variables_written': [svar.name for svar in f.function.all_state_variables_written()],
            'solidity_variables_read':[svar.name for svar in f.function.all_solidity_variables_read()],
            'conditions': [r._print() for r in f.conditions],
            
        }
        summary['functions'].append(f_summary)

    return summary

def calls(self):

    all_functions = [f for f in self.contract.functions + self.contract.modifiers]
    internal_calls = 0
    external_calls = 0
    for f in all_functions:
        internal_calls += len(f.internal_calls)
        external_calls += len(f.high_level_calls)
    return {
        'internal_calls': internal_calls,
        'external_calls': external_calls,
    }

def events(self):
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
    return summary


def andand_conditions(self):
    andand_if = []
    andand_require = []

    for f in self.functions:
        andand_if = [str(n) for n in f.andand_if_nodes]
        andand_require = [str(n) for n in f.andand_require_nodes]
        
    return {
        'andand_if': andand_if,
        'andand_require': andand_require,
    }

def collect_summary(self):
    #for d in self.detectors:
    #    self.summary.update(d.summary())

    self.summary.update(calls(self))
    self.summary.update(state_variables(self))
    self.summary.update(modifiers(self))
    self.summary.update(events(self))
    #self.summary.update(functions(self))
    self.summary.update(andand_conditions(self))