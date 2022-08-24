"""
{
    'contract_name':'',
    'address':'',
    'is_upgradeable_proxy':False,
    'is_upgradeable':False,
    'erc':'',
    'state_variables':[
        {
            'name':'' ,
            'type': '',
            'label': 'none',
            'rw':0000,

        }
    ],
    'functions':[
        {
            'name':'',
            'state_variables_read':[],
            'state_variables_written':[],
            'owner_in_condition':False,
        }
    ],
    erc_svars:{
        'owners':[],
        'bwList':[],
        'paused':[],
        'name':[],
        'symbol':[],
        'decimals':[],
        'totalSupply':[],
        'balances':[],
        'allowances':[],
        'ownerOf':[],
        'tokenApprovals':[],
        'operatorApprovals':[],
        'uri':[],
    },
    'erc_svars_rw':{
        'name':0000,
        'symbol':0000,
        'decimals':0000,
        'totalSupply':0000,
        'balances':0000,
        'allowances':0000,
        'ownerOf':0000,
        'tokenApprovals':0000,
        'operatorApprovals':0000,
        'uri':0000,
    },
    'lack_event_functions':[
        {
            'name':'',
            'owner_in_condition':False,
            'state_variables_written':[]
        }
    ],
}
"""
from naga.detectors import (VarLabel, DType, DMethod)
from naga.detectors.abstract_detector import _get_label_svars,_get_dtype_svars

def base_info(self):
    info = {}
    info.update(self.info)
    info.update({
        'is_upgradeable_proxy': self.is_upgradeable_proxy,
        'is_upgradeable': self.is_upgradeable,
        'erc': self.get_erc_str,
    })
    return info


def state_variable_summary(self):
    summary = {
        'svars': [],
        'svars_detection': {},
        'svars_label': {},
        'multistage_owners': [],
        'state_variables_label_rw': {},
        #'state_variables_rw': {},
    }

    for svar in self.exp_svars_dict.values(): 
        summary['svars'].append(svar.toJson())

    for dt in DType: 
        summary['svars_detection'][dt.value] = [svar.name for svar in _get_dtype_svars(self, dt)]
    for label in VarLabel: 
        summary['svars_label'][label.value] = [svar.name for svar in _get_label_svars(self, label)]

    summary['multistage_owners'] = [svar.name for svar in self.multistage_owners]

    return summary

def function_summary(self):
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

def modifier_summary(self):
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

def lack_event_summary(self):
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
            exp_svar = self.exp_svars_dict[svar]
            if exp_svar.dType != None:
                lack_event_user_erc_svars[exp_svar.dType.value].append({"function":f.function.full_name, "svar":svar.name})
            else:
                lack_event_user_erc_svars['None'].append({"function":f.function.full_name, "svar":svar.name})
    for f in self.lack_event_owner_functions:
        for svar in f.function.all_state_variables_written():
            exp_svar = self.exp_svars_dict[svar]
            if exp_svar.dType != None:
                lack_event_owner_erc_svars[exp_svar.dType.value].append({"function":f.function.full_name, "svar":svar.name})
            else:
                lack_event_owner_erc_svars['None'].append({"function":f.function.full_name, "svar":svar.name})
    
    summary['LE_user_svars'] = lack_event_user_erc_svars
    summary['LE_owner_svars'] = lack_event_owner_erc_svars

    for f in self.lack_event_functions:
        for svar in f.function.all_state_variables_written():
            summary['LE_rw'][self.exp_svars_dict[svar].rw].append({"function":f.function.full_name, "svar":svar.name})

    return summary

def contract_summary(self):
    summary = {}
    summary.update(base_info(self))
    summary.update(state_variable_summary(self))
    summary.update(function_summary(self))
    summary.update(modifier_summary(self))
    summary.update(lack_event_summary(self))
    return summary