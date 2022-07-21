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

from naga.core.erc import (ERC20_STATE_VARIAVLES, ERC721_STATE_VARIAVLES, ERC1155_STATE_VARIAVLES)

def get_common_labels():
    return ['owners', 'owners_1','owners_2','owners_3', 'bwList', 'paused']
def get_svar_labels():
    svar_labels = []
    for s in ERC20_STATE_VARIAVLES + ERC721_STATE_VARIAVLES + ERC1155_STATE_VARIAVLES:
        if s not in svar_labels:
            svar_labels.append(s[0])
    return svar_labels

def contract_summary(self):

    summary = {
        #'contract_name': self.contract.name,
        #'address': self.contract_address,
        #'compiler_version': self.compiler_version,
        #'ether_balance':self.ether_balance,
        #'txcount':self.txcount,
        #'date' :self.date,
        'is_upgradeable_proxy': self.is_upgradeable_proxy,
        'is_upgradeable': self.is_upgradeable,
        'erc': self.get_erc_str,
        'state_variables': [],
        'erc_svars':{},
        'erc_svars_rw':{},
        'svar_user_owner_rw':{ # user_read,user_write,owner_read,owner_write
            '0000':[],
            '0001':[], #
            '0010':[],
            '0011':[], #
            '0100':[],
            '0101':[], #
            '0110':[],
            '0111':[], #
            '1000':[],
            '1001':[], #
            '1010':[],
            '1011':[], #
            '1100':[],
            '1101':[], #
            '1110':[],
            '1111':[], #
        },
        'functions': [],
        'all_modifier_owners':[],
        'modifier_owners_used':[],
        'modifier_owners_unused':[],
        'modifiers':[],
        'onlyOwner_modifiers':[],
        'onlyRole_modifiers':[],
        'lack_event_functions': [],
        'lack_event_user_erc_svars':{},
        'lack_event_owner_erc_svars':{},
        'l_e_f_rw':{
            '0000':[],'0001':[], '0010':[],'0011':[], '0100':[],'0101':[], '0110':[],'0111':[], 
            '1000':[],'1001':[], '1010':[],'1011':[], '1100':[],'1101':[], '1110':[],'1111':[], 
        }
    }


    for svar in self.all_state_vars:
        svar_summary = {
            'name': svar.name,
            'type': str(svar.type),
            'label': 'none',
            'rw':self.svar_rw_dict[svar]
        }
        
        if svar in self.svar_label_dict:
            svar_summary['label'] = self.svar_label_dict[svar]

        summary['state_variables'].append(svar_summary)

    for f in self.functions:
        f_summary = {
            'name': f.function.full_name,
            #'parameters':f.function.parameters,
            'state_variables_read':[svar.name for svar in f.function.all_state_variables_read()],
            'state_variables_written': [svar.name for svar in f.function.all_state_variables_written()],
            'solidity_variables_read':[svar.name for svar in f.function.all_solidity_variables_read()],
            'conditions': [r._print() for r in f.conditions],
            'owner_in_condition': f in self.owner_in_condition_functions,
        }
        summary['functions'].append(f_summary)

    summary['all_modifier_owners'] = [svar.name for svar in self.all_modifier_owners]
    summary['modifier_owners_used'] = [svar.name for svar in self.modifier_owners_used]
    summary['modifier_owners_unused'] = [svar.name for svar in self.modifier_owners_unused]
    for m in self.contract.modifiers:
        modifier = {
            'name': m.name,
            'state_variables_read':[svar.name for svar in m.all_state_variables_read()],
            'state_variables_written': [svar.name for svar in m.all_state_variables_written()],
            'solidity_variables_read':[svar.name for svar in m.all_solidity_variables_read()],
        }
        summary['modifiers'].append(modifier)
    summary['onlyOwner_modifiers'] = [m.name for m in self.onlyOwner_modifiers]
    summary['onlyRole_modifiers'] = [m.name for m in self.onlyRole_modifiers]

    for f in self.lack_event_functions:
        summary['lack_event_functions'].append(f.function.name)
    
    svar_label_summary = dict()
    for svar_label in get_common_labels() + get_svar_labels():
        if svar_label in self.label_svars_dict:
            svar_label_summary[svar_label] =[ svar.name for svar in self.label_svars_dict[svar_label]]
        else:
            svar_label_summary[svar_label] = []
        summary['erc_svars'] = svar_label_summary

    svar_rw_summary = dict()
    for svar_label in get_svar_labels():
        if svar_label in self.label_svars_dict:
            svars = self.label_svars_dict[svar_label]
            if len(svars) > 0:
                svar_rw_summary[svar_label] = self.svar_rw_dict[svars[0]]
                continue
        svar_rw_summary[svar_label] = '0000'
    summary['erc_svars_rw'] = svar_rw_summary

    for svar in summary['state_variables']: # 统计每种读写情况出现的次数
        summary['svar_user_owner_rw'][svar['rw']].append(svar['name'])

    lack_event_user_erc_svars = dict() # 查找用户是写了什么变量
    lack_event_owner_erc_svars = dict() # 检查 owner 写了什么变量没有提示
    for svar_label in get_common_labels() + get_svar_labels():
        lack_event_user_erc_svars[svar_label] = []
        lack_event_owner_erc_svars[svar_label] = []
    lack_event_user_erc_svars['no_label'] = []
    lack_event_owner_erc_svars['no_label'] = []
    for f in self.lack_event_user_functions:
        for svar in f.function.all_state_variables_written():
            if svar in self.svar_label_dict: 
                lack_event_user_erc_svars[self.svar_label_dict[svar]].append({"function":f.function.full_name, "svar":svar.name})
            else: lack_event_user_erc_svars['no_label'].append({"function":f.function.full_name, "svar":svar.name})
    for f in self.lack_event_owner_functions:
        for svar in f.function.all_state_variables_written():
            if svar in self.svar_label_dict:
                lack_event_owner_erc_svars[self.svar_label_dict[svar]].append({"function":f.function.full_name, "svar":svar.name})
            else:
                lack_event_owner_erc_svars['no_label'].append({"function":f.function.full_name, "svar":svar.name})
    lack_event_owner_erc_svars['owners'] = lack_event_owner_erc_svars['owners_1'] + lack_event_owner_erc_svars['owners_2'] + lack_event_owner_erc_svars['owners_3']
    summary['lack_event_user_erc_svars'] = lack_event_user_erc_svars
    summary['lack_event_owner_erc_svars'] = lack_event_owner_erc_svars
    
    for f in self.lack_event_functions:
        for svar in f.function.all_state_variables_written():
            summary['l_e_f_rw'][self.svar_rw_dict[svar]].append({"function":f.function.full_name, "svar":svar.name})

    info_summary =  self.info # add info to summary
    info_summary.update(summary)
    #print(info_summary)
    return info_summary


            
# address, contract_name, is_upgradeable_proxy, is_upgradeable, erc, exist_ownership, exist_paused, owner_written_identities_num, svar_user_read_owner_update, svar_user_write_owner_update,lack_event_functions_num, lack_event_user_function_num, lack_event_owner_function_num,
def contract_summary2csv(self):
    line = {
        'contract_address':  self.summary['address'],
        'contract_name': self.summary['name'],
        'compiler_version': self.summary['compiler'],
        'is_upgradeable_proxy': self.summary['is_upgradeable_proxy'],
        'is_upgradeable': self.summary['is_upgradeable'],
        'erc': self.summary['erc'],
        'erc_force': self.summary['erc_force'],
        'naga_test_cost':self.summary['naga_test_cost'],
        'slither_compile_cost':self.summary['slither_compile_cost'],
        'proxy': self.summary['proxy'],
        'implementation':self.summary['implementation'],

        #### num ########
        'owners': len(self.summary['erc_svars']['owners']),
        'owners_1': len(self.summary['erc_svars']['owners_1']),
        'owners_2': len(self.summary['erc_svars']['owners_2']),
        'owners_3': len(self.summary['erc_svars']['owners_3']),
        'bwList': len(self.summary['erc_svars']['bwList']),
        'paused': len(self.summary['erc_svars']['paused']),
        ### user_owner read written ####
        'name': self.summary['erc_svars_rw']['name'],
        'symbol': self.summary['erc_svars_rw']['symbol'],
        'decimals': self.summary['erc_svars_rw']['decimals'],
        'totalSupply': self.summary['erc_svars_rw']['totalSupply'],
        'balances': self.summary['erc_svars_rw']['balances'],
        'allowances': self.summary['erc_svars_rw']['allowances'],
        'ownerOf': self.summary['erc_svars_rw']['ownerOf'],
        'tokenApprovals':self.summary['erc_svars_rw']['tokenApprovals'],
        'operatorApprovals': self.summary['erc_svars_rw']['operatorApprovals'],
        'uri': self.summary['erc_svars_rw']['uri'],
        ############################
        'svars_num': len(self.summary['state_variables']),
        'svars_xxx1_num': 0, # owner 写
        'svars_10x1_num': 0, # 用户只读的， owner 写
        'svars_x1x1_num': 0, # 用户读写的 owner 写

        'functions_num': len(self.summary['functions']),
        'read_functions_num': 0,
        'write_functions_num': 0,
        'owner_in_condition_functions_num': 0, # 

        'lack_event_functions_num': len(self.summary['lack_event_functions']),
        'lack_event_user_functions_num': 0, #
        'lack_event_owner_functions_num':  0, #

        #'l_e_f_user_update_owners': ,
        #'l_e_f_user_update_bwList': self.summary['lack_event_user_erc_svars']['bwList'],
        #'l_e_f_user_update_paused': self.summary['lack_event_user_erc_svars']['paused'],
        'l_e_f_user_update_name': self.summary['lack_event_user_erc_svars']['name'],
        'l_e_f_user_update_symbol': self.summary['lack_event_user_erc_svars']['symbol'],
        'l_e_f_user_update_decimals': self.summary['lack_event_user_erc_svars']['decimals'],
        'l_e_f_user_update_totalSupply': self.summary['lack_event_user_erc_svars']['totalSupply'],
        'l_e_f_user_update_balances': self.summary['lack_event_user_erc_svars']['balances'],
        'l_e_f_user_update_allowances': self.summary['lack_event_user_erc_svars']['allowances'],
        'l_e_f_user_update_ownerOf': self.summary['lack_event_user_erc_svars']['ownerOf'],
        'l_e_f_user_update_tokenApprovals':self.summary['lack_event_user_erc_svars']['tokenApprovals'],
        'l_e_f_user_update_operatorApprovals': self.summary['lack_event_user_erc_svars']['operatorApprovals'],
        'l_e_f_user_update_uri': self.summary['lack_event_user_erc_svars']['uri'],
        'l_e_f_user_update_no_label': self.summary['lack_event_user_erc_svars']['no_label'],

        'l_e_f_owner_update_owners': self.summary['lack_event_owner_erc_svars']['owners_1'] + self.summary['lack_event_owner_erc_svars']['owners_2'] + self.summary['lack_event_owner_erc_svars']['owners_3'],
        'l_e_f_owner_update_owners_1': self.summary['lack_event_owner_erc_svars']['owners_1'],
        'l_e_f_owner_update_owners_2': self.summary['lack_event_owner_erc_svars']['owners_2'],
        'l_e_f_owner_update_owners_3': self.summary['lack_event_owner_erc_svars']['owners_3'],

        'l_e_f_owner_update_bwList':self.summary['lack_event_owner_erc_svars']['bwList'],
        'l_e_f_owner_update_paused': self.summary['lack_event_owner_erc_svars']['paused'],
        'l_e_f_owner_update_name': self.summary['lack_event_owner_erc_svars']['name'],
        'l_e_f_owner_update_symbol': self.summary['lack_event_owner_erc_svars']['symbol'],
        'l_e_f_owner_update_decimals': self.summary['lack_event_owner_erc_svars']['decimals'],
        'l_e_f_owner_update_totalSupply': self.summary['lack_event_owner_erc_svars']['totalSupply'],
        'l_e_f_owner_update_balances': self.summary['lack_event_owner_erc_svars']['balances'],
        'l_e_f_owner_update_allowances': self.summary['lack_event_owner_erc_svars']['allowances'],
        'l_e_f_owner_update_ownerOf': self.summary['lack_event_owner_erc_svars']['ownerOf'],
        'l_e_f_owner_update_tokenApprovals':self.summary['lack_event_owner_erc_svars']['tokenApprovals'],
        'l_e_f_owner_update_operatorApprovals': self.summary['lack_event_owner_erc_svars']['operatorApprovals'],
        'l_e_f_owner_update_uri': self.summary['lack_event_owner_erc_svars']['uri'],
        'l_e_f_owner_update_no_label': self.summary['lack_event_owner_erc_svars']['no_label'],

        'l_e_f_rw_xxx1_num': 0,
        'l_e_f_rw_10x1_num': 0,
        'l_e_f_rw_x1x1_num': 0,

    }

    svars_xxx1_num = 0
    svars_10x1_num = 0
    svars_x1x1_num = 0
    for svar in self.summary['state_variables']:
        if svar['rw'][3] == '1':
            svars_xxx1_num += 1
            if svar['rw'][0] == '1' and svar['rw'][1] == '0':
                svars_10x1_num += 1
            if svar['rw'][1] == '1':
                svars_x1x1_num += 1
    line['svars_xxx1_num'] = svars_xxx1_num
    line['svars_10x1_num'] = svars_10x1_num
    line['svars_x1x1_num'] = svars_x1x1_num

    read_functions_num = 0
    write_functions_num = 0
    owner_in_condition_functions_num = 0
    for f in self.summary['functions']:
        if len(f['state_variables_read']) > 0 and len(f['state_variables_written']) == 0:
            read_functions_num += 1
        if len(f['state_variables_written']) > 0:
            write_functions_num += 1
        if f['owner_in_condition']:
            owner_in_condition_functions_num += 1
    line['read_functions_num'] = read_functions_num
    line['write_functions_num'] = write_functions_num
    line['owner_in_condition_functions_num'] = owner_in_condition_functions_num

    lack_event_user_functions_num = 0
    lack_event_owner_functions_num = 0
    for f in self.summary['lack_event_functions']:
        if f['owner_in_condition']:
            lack_event_owner_functions_num += 1
        else:
            lack_event_user_functions_num += 1
    line['lack_event_user_functions_num'] = lack_event_user_functions_num
    line['lack_event_owner_functions_num'] = lack_event_owner_functions_num

    l_e_f_rw_xxx1_num = 0
    l_e_f_rw_10x1_num = 0
    l_e_f_rw_x1x1_num = 0
    for k,v in self.summary['l_e_f_rw'].items():
        if k[3] == '1':
            l_e_f_rw_xxx1_num += v
            if k[0] == '1' and k[1] == '0':
                l_e_f_rw_10x1_num += v
            if k[1] == '1':
                l_e_f_rw_x1x1_num += v
    line['l_e_f_rw_xxx1_num'] = l_e_f_rw_xxx1_num
    line['l_e_f_rw_10x1_num'] = l_e_f_rw_10x1_num
    line['l_e_f_rw_x1x1_num'] = l_e_f_rw_x1x1_num

    titles = []
    values = []
    for k,v in line.items():
        titles.append(k)
        values.append(str(v))

    return line, ','.join(titles), ','.join(values)