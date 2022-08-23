from typing import List, Dict,Optional
from slither.core.variables.state_variable import StateVariable
from .abstract_detector import (AbstractDetector, VarLabel, DType, DMethod,_set_state_vars_label,_get_no_label_svars,_get_label_svars)

#  state variable name, return function signature, type, possible names (lower names)
ERC20_STATE_VARIAVLES = [
    (VarLabel._name,DType.METADATA,'name()', 'string', ['name']),
    (VarLabel._symbol,DType.METADATA,'symbol()', 'string', ['symbol']),
    (VarLabel._decimals,DType.METADATA,'decimals()', 'uint', ['decimals','decimal']),
    (VarLabel._totalSupply,DType.UNDEFINED,'totalSupply()', 'uint', ['totalsupply','supply']),
    (VarLabel._balances,DType.UNDEFINED,'balanceOf(address)', 'mapping(address => uint256)', ['balances','balance']),
    (VarLabel._allowances,DType.UNDEFINED,'allowance(address,address)','mapping(address => mapping(address => uint256))',['allowances','allowance']),
]

ERC721_STATE_VARIAVLES = [
    (VarLabel._name,DType.METADATA,'name()', 'string',  ['name']),
    (VarLabel._symbol,DType.METADATA,'symbol()', 'string',['symbol']),
    (VarLabel._owners,DType.UNDEFINED,'ownerOf(uint256)','mapping(uint256 => address)',['owners'],), # 这个owner不是管理员 owner
    (VarLabel._balances,DType.UNDEFINED,'balanceOf(address)','mapping(address => uint256)',['balances','balance']),
    (VarLabel._tokenApprovals,DType.UNDEFINED,'getApproved(uint256)','mapping(address => uint256)',['tokenapprovals','tokenapproval']),
    (VarLabel._operatorApprovals,DType.UNDEFINED,'isApprovedForAll(address, address)','mapping(address => mapping(address => bool))',['operatorapprovals','operatorapproval']),
    (VarLabel._uri,'tokenURI(uint256)','string',['baseuri','uri'])
]

ERC1155_STATE_VARIAVLES = [
    (VarLabel._balances,DType.UNDEFINED,'balanceOf(address, uint256)','mapping(uint256 => mapping(address => uint256))',['balances','balance']),
    (VarLabel._operatorApprovals,DType.UNDEFINED,'isApprovedForAll(address, address)','mapping(address => mapping(address => bool))',['_operatorapprovals','operatorapproval']),
    (VarLabel._uri,DType.METADATA,'uri(uint256)','string',['uri']),
    (VarLabel._totalSupply,DType.UNDEFINED,'totalSupply()', 'mapping(uint256 => uint256)', ['totalsupply','supply'])
]

exclude_stateVaribles = [
    # type,name
    ('bytes16','_HEX_SYMBOLS')
]

'''
    首先检测是否继承了ERC20或者ERC721或者ERC1155
    然后检测 getter 方法
    最后检测参数名称和值
'''
def _detect_inheritance(self,token,ERC_METADATA):
    if not any(
        c
        for c in self.contract.inheritance
        if c.name == token
    ):
        return
    for em in ERC_METADATA:
        for svar in self.all_state_vars:
            if svar.name == em[0].name and str(svar.type).startswith(em[3]):
                _set_state_vars_label(self,[svar],em[0],em[1],DMethod.INHERITANCE)
                break

def _detect_getter(self,ERC_METADATA):
    for em in ERC_METADATA:
        return_funs = [f for f in self.functions if f.function.full_name == em[2]]
        if len(return_funs) == 0 : continue
        for return_fun in return_funs:
            svars = return_fun.return_var_group.state_vars
            if len(svars) == 0: continue
            if len(svars) == 1:
                _set_state_vars_label(self,svars,em[0],em[1],DMethod.GETTER)
                continue

            match_name = [svar for svar in svars if svar.name.lower().replace('_','') in em[4]]
            if len(match_name) == 1:
                _set_state_vars_label(self,match_name,em[0],em[1],DMethod.GETTER)
                continue
            
            match_type = [svar for svar in svars if str(svar.type).startswith(em[3])]
            if len(match_type) == 1:
                _set_state_vars_label(self,match_type,em[0],em[1],DMethod.GETTER)
                continue


def _detect_name(self,ERC_METADATA):
    no_label_svars = _get_no_label_svars(self)
    for em in ERC_METADATA:
        if _get_label_svars(self,em[0]):
            continue
        match_name = [svar for svar in no_label_svars if svar.name.lower().replace('_','') in em[4]]
        if len(match_name) == 1:
            _set_state_vars_label(self,match_name,em[0],em[1],DMethod.NAME)
            continue
        match_name_type = [svar for svar in match_name if str(svar.type).startswith(em[3])]
        if len(match_name_type) == 1:
            _set_state_vars_label(self,match_name_type,em[0],em[1],DMethod.NAME)
            continue

class ERCMetadata(AbstractDetector):
    def __init__(self,cexp,erc) -> None:
        super().__init__(cexp)
        if erc == 'erc20':
            self.ERC_METADATA = ERC20_STATE_VARIAVLES
            self.token = 'ERC20'
        elif erc == 'erc721':
            self.ERC_METADATA = ERC721_STATE_VARIAVLES
            self.token = 'ERC721'
        elif erc == 'erc1155':
            self.ERC_METADATA = ERC1155_STATE_VARIAVLES
            self.token = 'ERC1155'

    def _detect(self):
        _detect_inheritance(self.cexp,self.token,self.ERC_METADATA)
        _detect_getter(self.cexp,self.ERC_METADATA)
        #_detect_name(self.cexp,self.ERC_METADATA)
        #_update_state_vars_(self.cexp)

    def summary(self):
        return {}