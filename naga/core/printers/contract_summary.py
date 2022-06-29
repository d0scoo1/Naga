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
            'is_user_read': 'none',
            'is_user_written': 'none',
            'is_owner_read': 'none',
            'is_owner_written': 'none',
        }
    ],
    'functions':[
        {
            'name':'',
            'only_read':False,
            'owner_in_require':False,
        }
    ],
    'lack_event_functions':[
        {
            'name':'',
            'owner_in_require':False,
            'state_variables_written':[]
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
    }
}
"""

from naga.core.erc import (ERC20_STATE_VARIAVLES, ERC721_STATE_VARIAVLES, ERC1155_STATE_VARIAVLES)

def get_common_labels():
    return ['owners', 'bwList', 'paused']
def get_svar_labels():
    svar_labels = []
    for s in ERC20_STATE_VARIAVLES + ERC721_STATE_VARIAVLES + ERC1155_STATE_VARIAVLES:
        svar_labels.append(s[0])
    return list(set(svar_labels))

import json

def contract_summary(self):
    summary = {
        'contract_name': self.contract.name,
        'address': self.contract_address,
        'is_upgradeable_proxy': self.is_upgradeable_proxy,
        'is_upgradeable': self.is_upgradeable,
        'erc': self.get_erc_str,
        'state_variables': [],
        'functions': [],
        'lack_event_functions': [],
        'erc_svars':{},
        'erc_svars_rw':{},
        'svar_user_owner_rw':{ # 我们只关心用户读写和owner 写， 也就是末位为 1 的
            '0000':0,
            '0001':0, #
            '0010':0,
            '0011':0, #
            '0100':0,
            '0101':0, #
            '0110':0,
            '0111':0, #
            '1000':0,
            '1001':0, #
            '1010':0,
            '1011':0, #
            '1100':0,
            '1101':0, #
            '1110':0,
            '1111':0, #
        },
        'lack_event_user_erc_svars':{},
        'lack_event_owner_erc_svars':{},
        'lack_event_user_owner_rw':{
            '0000':0,'0001':0, '0010':0,'0011':0, '0100':0,'0101':0, '0110':0,'0111':0, 
            '1000':0,'1001':0, '1010':0,'1011':0, '1100':0,'1101':0, '1110':0,'1111':0, 
        }

    }

    for svar in self.all_state_vars:
        svar_summary = {
            'name': svar.name,
            'type': str(svar.type),
            'label': 'none',
            'is_user_read': 'none',
            'is_user_written': 'none',
            'is_owner_read': 'none',
            'is_owner_written': 'none',
            'rw':'0000'
        }
        if svar in self.svar_label_dict:
            svar_summary['label'] = self.svar_label_dict[svar]
        fs_u_r,fs_u_w,fs_o_r,fs_o_w = self.get_svar_read_written_functions(svar)
        svar_summary['is_user_read'] = len(fs_u_r) > 0
        svar_summary['is_user_written'] = len(fs_u_w) > 0
        svar_summary['is_owner_read'] = len(fs_o_r) > 0
        svar_summary['is_owner_written'] = len(fs_o_w) > 0
        svar_summary['rw'] = self.svar_rw_dict[svar]

        summary['state_variables'].append(svar_summary)

    for f in self.functions:
        f_summary = {
            'name': f.function.name,
            'state_variables_read':[svar.name for svar in f.function.all_state_variables_read()],
            'state_variables_written': [svar.name for svar in f.function.all_state_variables_written()],
            'owner_in_require': f in self.owner_in_require_functions,
        }
        summary['functions'].append(f_summary)
    for f in self.lack_event_functions:
        f_summary = {
            'name': f.function.name,
            'owner_in_require': f in self.owner_in_require_functions,
            'state_variables_written': [],
        }
        for svar in f.function.all_state_variables_written():
            f_summary['state_variables_written'].append(svar.name)
        summary['lack_event_functions'].append(f_summary)
    
    svar_label_summary = {}
    for svar_label in get_common_labels() + get_svar_labels():
        if svar_label in self.label_svars_dict:
            svar_label_summary[svar_label] =[ svar.name for svar in self.label_svars_dict[svar_label]]
        else:
            svar_label_summary[svar_label] = []
        summary['erc_svars'] = svar_label_summary

    svar_rw_summary = {}
    for svar_label in get_svar_labels():
        if svar_label in self.label_svars_dict:
            svars = self.label_svars_dict[svar_label]
            if len(svars) > 0:
                svar_rw_summary[svar_label] = self.svar_rw_dict[svars[0]]
                continue
        svar_rw_summary[svar_label] = '0000'
    summary['erc_svars_rw'] = svar_rw_summary

    for svar in summary['state_variables']: # 统计每种读写情况出现的次数
        summary['svar_user_owner_rw'][svar['rw']] += 1

    lack_event_user_erc_svars = {} # 查找用户是写了什么变量
    lack_event_owner_erc_svars = {} # 检查 owner 写了什么变量没有提示
    for svar_label in get_common_labels() + get_svar_labels():
        lack_event_user_erc_svars[svar_label] = 0
        lack_event_owner_erc_svars[svar_label] = 0
    lack_event_user_erc_svars['none'] = 0
    lack_event_owner_erc_svars['none'] = 0
    for f in self.lack_event_user_functions:
        for svar in f.function.all_state_variables_written():
            if svar in self.svar_label_dict: 
                lack_event_user_erc_svars[self.svar_label_dict[svar]] += 1
            else: lack_event_user_erc_svars['none'] += 1
    for f in self.lack_event_owner_functions:
        for svar in f.function.all_state_variables_written():
            if svar in self.svar_label_dict:
                lack_event_owner_erc_svars[self.svar_label_dict[svar]] += 1
            else:
                lack_event_owner_erc_svars['none'] += 1
    summary['lack_event_user_erc_svars'] = lack_event_user_erc_svars
    summary['lack_event_owner_erc_svars'] = lack_event_owner_erc_svars
    
    for f in self.lack_event_functions:
        for svar in f.function.all_state_variables_written():
            summary['lack_event_user_owner_rw'][self.svar_rw_dict[svar]] += 1

    return summary


# address, contract_name, is_upgradeable_proxy, is_upgradeable, erc, exist_ownership, exist_paused, owner_written_identities_num, svar_user_read_owner_update, svar_user_write_owner_update,lack_event_functions_num, lack_event_user_function_num, lack_event_owner_function_num,
def contract_csv_summary(self):
    line = {
        'address':  self.contract_address,
        'contract_name': self.contract.name,
        'is_upgradeable_proxy': self.is_upgradeable_proxy,
        'is_upgradeable': self.is_upgradeable,
        'erc': self.get_erc_str,
        'owners_num': len(self.label_svars_dict['owners']),
        'bwList': len(self.label_svars_dict['bwList']),
        'paused': len(self.label_svars_dict['paused']),

        'other_svars_user_read_owner_updated':0,
        'other_svars_user_written_owner_updated':0,
        'total_svars_user_read_owner_updated':0,
        'total_svars_user_written_owner_updated':0,

        'state_vars_user_only_read_owner_updated': len(self.state_vars_user_only_read_owner_updated),
        'state_vars_user_written_owner_updated': len(self.state_vars_user_written_owner_updated),
        'lack_event_functions_num': len(self.lack_event_functions),
        'lack_event_user_functions_num': len(self.lack_event_user_functions),
        'lack_event_owner_functions_num': len(self.lack_event_owner_functions),
        'lack_event_owner_update_owner':0, # TODO:
        'lack_event_owner_update_paused':0,
        'lack_event_owner_update_bwList':0,
        'lack_event_owner_update_name':0,
        'lack_event_owner_update_totalsupply':0,
        'lack_event_owner_update_balance':0,
        'lack_event_owner_update_allowance':0,
        'lack_event_other_svars_owner_updated':0,
        'lack_event_total_svars_owner_updated':0,

    }