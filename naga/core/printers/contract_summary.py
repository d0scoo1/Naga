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

def base_info(self):
    info = {}
    info.update(self.info)
    info.update({
        'is_upgradeable_proxy': self.is_upgradeable_proxy,
        'is_upgradeable': self.is_upgradeable,
        'erc': self.get_erc_str,
    })
    return info

from naga.core.openzeppelin import (ERC20_STATE_VARIAVLES, ERC721_STATE_VARIAVLES, ERC1155_STATE_VARIAVLES)

def get_common_labels():
    return ['owner', 'role', 'bwList', 'paused','unfair_uint']
def get_svar_labels():
    svar_labels = []
    for s in ERC20_STATE_VARIAVLES + ERC721_STATE_VARIAVLES + ERC1155_STATE_VARIAVLES:
        if s not in svar_labels:
            svar_labels.append(s[0])
    return svar_labels

def state_variable_summary(self):
    summary = {
        'state_variables': [],
        'state_variables_label': {},
        'multistage_owners': [],
        'state_variables_label_rw': {},
        #'state_variables_rw': {},
    }

    for k,v in self.exp_svars_dict.items():
        summary['state_variables'].append({
            'name': str(k),
            'type': str(k.type),
            'label': v['label'],
            'rw': v['rw'],
        })
    
    for svar_label in get_common_labels() + get_svar_labels():
        summary['state_variables_label'][svar_label] = [str(svar) for svar in self.exp_svars_dict if self.exp_svars_dict[svar]['label'] == svar_label]
    summary['state_variables_label']['access'] = summary['state_variables_label']['owner'] + summary['state_variables_label']['role']
    
    summary['multistage_owners'] = [svar.name for svar in self.multistage_owners]

    for svar_label in get_svar_labels():
        svars = [svar for svar in self.exp_svars_dict if self.exp_svars_dict[svar]['label'] == svar_label]
        if len(svars) > 0:
            summary['state_variables_label_rw'][svar_label] = self.exp_svars_dict[svars[0]]['rw']
        else:
            summary['state_variables_label_rw'][svar_label] = '0000'

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
    summary = {'all_modifiers':[],
    'access_modifiers':[ m.name for m in self.access_modifiers],
    'onlyOwner_modifiers':[svar.name for svar in self.onlyOwner_modifiers],
    'onlyRole_modifiers':[svar.name for svar in self.onlyRole_modifiers],
    }

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
    for svar_label in get_common_labels() + get_svar_labels():
        lack_event_user_erc_svars[svar_label] = []
        lack_event_owner_erc_svars[svar_label] = []
    lack_event_user_erc_svars['no_label'] = []
    lack_event_owner_erc_svars['no_label'] = []
    for f in self.lack_event_user_functions:
        for svar in f.function.all_state_variables_written():
            exp_svar = self.exp_svars_dict[svar]
            if exp_svar['label'] != 'no_label':
                lack_event_user_erc_svars[exp_svar['label']].append({"function":f.function.full_name, "svar":svar.name})
            else:
                lack_event_user_erc_svars['no_label'].append({"function":f.function.full_name, "svar":svar.name})
    for f in self.lack_event_owner_functions:
        for svar in f.function.all_state_variables_written():
            exp_svar = self.exp_svars_dict[svar]
            if exp_svar['label'] != 'no_label':
                lack_event_owner_erc_svars[exp_svar['label']].append({"function":f.function.full_name, "svar":svar.name})
            else:
                lack_event_owner_erc_svars['no_label'].append({"function":f.function.full_name, "svar":svar.name})
    lack_event_owner_erc_svars['access'] = lack_event_owner_erc_svars['owner'] + lack_event_owner_erc_svars['role']
    summary['LE_user_svars'] = lack_event_user_erc_svars
    summary['LE_owner_svars'] = lack_event_owner_erc_svars
    
    for f in self.lack_event_functions:
        for svar in f.function.all_state_variables_written():
            summary['LE_rw'][self.exp_svars_dict[svar]['rw']].append({"function":f.function.full_name, "svar":svar.name})

    return summary

def detect_method_summary(self):
    summary ={
        #openzeppelin 直接检测出的 owner / role, paused
        'inheritance_detected':{},
        # modifier 直接检测出的 owner / role
        'modifier_detected':{
            'owner':[svar.name for svar in self.modifiers_detected_owners],
            'role':[svar.name for svar in self.modifiers_detected_roles],
        },
        'im_detected':{
            'owner':[],
            'role':[],
        },
        'detect_erc_state_vars_by_return':[],
        'detect_erc_state_vars_by_name':[],
    }

    for label,svars in self.inheritance_detected_svars.items():
        summary['inheritance_detected'][label] = [svar.name for svar in svars]
    
    ### 不同的contracts 可能存在相同的 stateVariable name，因此不能直接使用变量名来 list(set())
    summary['im_detected']['owner'] = [svar.name for svar in list(set(self.modifiers_detected_owners + self.inheritance_detected_svars['owner']))]
    summary['im_detected']['role'] = [svar.name for svar in list(set(self.modifiers_detected_roles + self.inheritance_detected_svars['role']))]
    

    summary['detect_erc_state_vars_by_return'] = [svar.name for svar in self.detect_erc_state_vars_by_return]
    summary['detect_erc_state_vars_by_name'] = [svar.name for svar in self.detect_erc_state_vars_by_name]

    return summary

def contract_summary(self):
    summary = {}
    summary.update(base_info(self))
    summary.update(state_variable_summary(self))
    summary.update(function_summary(self))
    summary.update(modifier_summary(self))
    summary.update(lack_event_summary(self))
    summary.update(detect_method_summary(self))
    return summary