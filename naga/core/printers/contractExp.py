"""
{
    'contract_name':'',
    'address':'',
    'is_upgradeable_proxy':False,
    'is_upgradeable':False,
    'erc':'',
    'state_variables':[
        {
            'name':
            'type':'',
            'label':'',
            'is_user_read':False,
            'is_user_written':False,
            'is_owner_read':False,
            'is_owner_written':False,
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
    
}
"""

import json

def contract_json_summary(self):
    summary = {
        'contract_name': self.contract.name,
        'address': self.contract_address,
        'is_upgradeable_proxy': self.is_upgradeable_proxy,
        'is_upgradeable': self.is_upgradeable,
        'erc': self.get_erc_str,
        'state_variables': [],
        'functions': [],
        'lack_event_functions': [],
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
        }
        if svar in self.svar_label_dict:
            svar_summary['label'] = self.svar_label_dict[svar]
        fs_u_r,fs_u_w,fs_o_r,fs_o_w = self.get_svar_read_written_functions(svar)
        svar_summary['is_user_read'] = len(fs_u_r) > 0
        svar_summary['is_user_written'] = len(fs_u_w) > 0
        svar_summary['is_owner_read'] = len(fs_o_r) > 0
        svar_summary['is_owner_written'] = len(fs_o_w) > 0

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
    return json.dumps(summary,indent=4)


# address, contract_name, is_upgradeable_proxy, is_upgradeable, erc, exist_ownership, exist_paused, owner_written_identities_num, svar_user_read_owner_update, svar_user_write_owner_update,lack_event_functions_num, lack_event_user_function_num, lack_event_owner_function_num,
def contract_csv_summary(self):
    line = {
        'address':  self.contract_address,
        'contract_name': self.contract.name,
        'is_upgradeable_proxy': self.is_upgradeable_proxy,
        'is_upgradeable': self.is_upgradeable,
        'erc': self.get_erc_str,
        'owners_num': len(self.label_svars_dict['owners']),
        'bwList': len(self.label_svars_dict['bwList']) > 0,
        'paused': len(self.label_svars_dict['paused']) > 0,
        'name_owner_updated':False,
        'totalsupply_owner_updated':False,
        'balance_owner_updated':False,
        
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