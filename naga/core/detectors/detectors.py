from typing import List, Dict,Optional
from slither.core.variables.state_variable import StateVariable
from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.mapping_type import MappingType

'''
from enum import Enum
class StateVarLabel(Enum):
    UNKNOWN = 0x0
    OWNERS = 0x10001
    BWLIST = 0x10002
    PAUSED = 0x10003
    NAME = 0x20001
    SYMBOL = 0x20002
    DECIMALS = 0x20003
    TOTAL_SUPPLY = 0x20004
    BALANCES = 0x20005
    ALLOWANCES = 0x20006
    OWNER_OF = 0x30001
    TOKEN_APPROVALS = 0x30001
    OPERATOR_APPROVALS = 0x30002
    URI = 0x30003


    def __str__(self):
        if self == StateVarLabel.UNKNOWN:
            return "UNKNOWN"
        elif self == StateVarLabel.OWNERS:
            return "OWNERS"
        elif self == StateVarLabel.BWLIST:
            return "BWLIST"
        elif self == StateVarLabel.PAUSED:
            return "PAUSED"
        elif self == StateVarLabel.NAME:
            return "NAME"
        elif self == StateVarLabel.SYMBOL:
            return "SYMBOL"
        elif self == StateVarLabel.DECIMALS:
            return "DECIMALS"
        elif self == StateVarLabel.TOTAL_SUPPLY:
            return "TOTAL_SUPPLY"
        elif self == StateVarLabel.BALANCES:
            return "BALANCES"
        elif self == StateVarLabel.ALLOWANCES:
            return "ALLOWANCES"
        elif self == StateVarLabel.OWNER_OF:
            return "OWNER_OF"
        elif self == StateVarLabel.TOKEN_APPROVALS:
            return "TOKEN_APPROVALS"
        elif self == StateVarLabel.OPERATOR_APPROVALS:
            return "OPERATOR_APPROVALS"
        elif self == StateVarLabel.URI:
            return "URI"

        return "None"
'''

def detect_owners_bwList(self):
    """
    Search owners, black list, white list.

    搜索所有的 owners
    1. owner 需要是 state variable
    2. owner 的类型是 address 或 mapping()
    3. owner 如果存在写函数，
        3.1 为构造函数
    或 3.2 写函数被 require约束，且约束条件中仅包含 state var, msg.sender
    """

    # 检索所有的 function 查看是否有符合类型的 state variable
    all_candidates = [svar for f in self.functions for svar in f.owner_candidates]

    owner_candidates = []
    for svar in all_candidates:
        # 检查 candidates 所有的写函数是否被 owner 约束
         # 如果不是构造函数，并且不存在 owner candidates
        if any(len(f.owner_candidates) == 0 and not f.is_constructor_or_initializer
            for f in self.state_var_written_functions_dict[svar]
            ):
            continue
        owner_candidates.append(svar)

    # 检查每个 owner_candidate 依赖的 owner 是否也属于 owner_candidate
    # 首先找出自我依赖的，然后检查剩余的是否依赖于自我依赖
    owners_1 = []
    for svar in owner_candidates:
        # 检查是否存在自我依赖：owner 的写函数是 owner in require functions 的子集 (上一步中，我们已经确定每个 owner 的写函数都被 owner_candidates 约束)
        read_in_require_funcs = self.state_var_read_in_require_functions_dict[svar]
        # 去掉 written_funcs 中的构造函数
        written_funcs =[f for f in self.state_var_written_functions_dict[svar] if not f.is_constructor_or_initializer ]

        if len(set(written_funcs) - set(read_in_require_funcs)) > 0:
            continue
        owners_1.append(svar)
    
    # 检查剩余的 owner 是否依赖于 owner
    # 找出每个 candidates 的写函数，得到他们写函数的约束的 owner,如果约束 owner 存在于 owner_1 + 自己 中，则成立，
    owners_1 = list(set(owners_1))
    owner_candidates = list(set(owner_candidates)-set(owners_1))

    owners_2 = []
    for svar in owner_candidates:
        dep_owners = []
        for t_wf in [f for f in self.state_var_written_functions_dict[svar] if not f.is_constructor_or_initializer]: dep_owners += t_wf.owner_candidates # 这里 构造函数不存在 owner_candidates
        if len(set(dep_owners) - set(owners_1) - {svar}) == 0: # 如果越来的 owner_1 仅包括 owner_1 + 自己，则成立
            owners_2.append(svar)

    owner_candidates = list(set(owner_candidates)-set(owners_2))
    owners_3 = []
    owners_3_index = 0
    while owners_3_index < len(owner_candidates): # 最大深度不过是依次依赖
        for svar in owner_candidates:
            dep_owners = []
            for t_wf in [f for f in self.state_var_written_functions_dict[svar] if not f.is_constructor_or_initializer]: dep_owners += t_wf.owner_candidates # 这里 构造函数不存在 owner_candidates
            if len(set(dep_owners) - set(owners_1 + owners_2 + owners_3) - {svar}) == 0:
                owners_3.append(svar)
        owners_3_index += 1

    #If there are mappings in the owners, check whether these state variables are black/white Lists.
    mapping_owners = []
    owners = owners_1 + owners_2 + owners_3
    for svar in owners:
        if isinstance(svar.type, MappingType):
            mapping_owners.append(svar)
    if len(mapping_owners) == 0:
        self.label_svars_dict.update({'owners': owners,'owners_1':owners_1,'owners_2':owners_2, 'owners_3':owners_3,'bwList':[]})
        return

    # blackList / whiteList 和 admin 有相同的模式，因此，需要排除 blackList / whiteList
    # 具体而言，我们检查 token_written_functions 中出现的 mapping owner candidates，如果和 owners 中匹配，我们认为它是 blackList / whiteList 而不是 owner
    bwList = []
    bwList_candidates = [svar for f in self.token_written_functions for svar in f.owner_candidates ]
    for svar in list(set(bwList_candidates)):
        #if isinstance(svar.type, MappingType) and svar.type.type_from == ElementaryType('address') and svar.type.type_to == ElementaryType('bool'):
        if svar in mapping_owners:
            bwList.append(svar)

    self.label_svars_dict.update({
        'owners':list(set(owners)-set(bwList)),
        'owners_1':list(set(owners_1)-set(bwList)),
        'owners_2':list(set(owners_2)-set(bwList)),
        'owners_3':list(set(owners_3)-set(bwList)),
        'bwList':list(set(bwList))
        })

def detect_paused(self):
    """
    Before Functions: detect_owners_bwList
    搜索所有的 paused
    paused 符合以下特点，出现在 tranfer 的 require 中（没有 local variables 出现在 require 中），bool 类型，只有 owner 可以修改
    """
    paused_candidates = []
    for svar in self.state_vars_user_only_read_owner_updated:
        if svar.type == ElementaryType('bool'):
            paused_candidates.append(svar)

    paused = []
    for svar in list(set(paused_candidates)):
        funcs_sigs = [f.function.full_name for f in self.state_var_read_in_require_functions_dict[svar] ]
        if len(set(funcs_sigs) & set(self.token_write_function_sigs)) > 0: # 如果变量 require function 出现在 token 写函数中
            paused.append(svar)
    
    self.label_svars_dict.update({'paused':paused})

def _search_one_state_var_in_return(self, f_sig:str, type_str:str, svar_lower_names:List[str]) -> StateVariable:
    """ 
    查找 return 中的返回值
    """
    func = None
    for f in self.functions:
        if f.function.full_name == f_sig:
            func = f
            break

    candidates = []
    if func is not None:
        candidates = [svar for svar in func.return_var_group.state_vars if str(svar.type).startswith(type_str)]
        if len(candidates) == 1:
            return [candidates[0]]

    for svar in candidates + self.all_state_vars:
        for name in svar_lower_names:
            if name in svar.name.lower():
                return [svar]
    return []

"""
    Search common state variables in the ERC 20 721 1155
"""
from naga.core.erc import (ERC20_STATE_VARIAVLES,ERC721_STATE_VARIAVLES,ERC1155_STATE_VARIAVLES)

def _detect_erc_state_vars(self, erc_state_vars):
    results = dict()
    for v in erc_state_vars:
        results[v[0]] = _search_one_state_var_in_return(self,v[1],v[2],v[3])
    return results

def detect_erc20_state_vars(self):
    rs = _detect_erc_state_vars(self,ERC20_STATE_VARIAVLES)

    self.label_svars_dict.update(rs)

def detect_erc721_state_vars(self):
    rs = _detect_erc_state_vars(self,ERC721_STATE_VARIAVLES)
    self.label_svars_dict.update(rs)

def detect_erc1155_state_vars(self):
    rs = _detect_erc_state_vars(self,ERC1155_STATE_VARIAVLES)
    self.label_svars_dict.update(rs)

'''
def detect_unfair_settings(self):
    """
        Before Functions: detect_owners_bwList, detect_paused, detect_erc_state_vars
        检查所有剩下的 owner 可以修改的 state vars
    """
    unfair_settings = []
    for svar in self.state_vars_owner_updated:
        unfair_settings.append(svar)

    marked_svars = []
    for svars in self.label_svars_dict.values():
        marked_svars += svars
    unfair_settings = list(set(unfair_settings) - set(marked_svars))

    self.label_svars_dict.update({'unfair_settings':unfair_settings})
'''

def detect_lack_event_functions(self):
    """
    Before Functions: detect_owners_bwList
    如果一个 function 写了 state variable，则应当发送一个 event，提醒用户，这里寻找缺少的 event 的 function。
    我们并不考虑 event 的参数，关于 event 和实际操作不一致的问题：TokenScope: Automatically Detecting Inconsistent Behaviors of Cryptocurrency Tokens in Ethereum
    """

    lack_event_owner_functions = []
    lack_event_user_functions = []
    for f in self.state_var_written_functions:
        if not f.is_constructor_or_initializer and len(f.events) == 0:
            if f in self.owner_in_require_functions:
                lack_event_owner_functions.append(f)
            else:
                lack_event_user_functions.append(f)
    
    self.lack_event_functions = lack_event_owner_functions + lack_event_user_functions
    self.lack_event_owner_functions = lack_event_owner_functions
    self.lack_event_user_functions = lack_event_user_functions

