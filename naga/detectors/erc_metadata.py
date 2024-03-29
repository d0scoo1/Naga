from typing import List, Dict,Optional
from slither.core.variables.state_variable import StateVariable
from slither.slithir.variables.state_variable import StateIRVariable
from .abstract_detector import *

#  state variable name, return function signature, type, possible names (lower names)
ERC20_STATE_VARIAVLES = [
    (VarLabel._name,DType.METADATA,'name()', 'string', ['name']),
    (VarLabel._symbol,DType.METADATA,'symbol()', 'string', ['symbol']),
    (VarLabel._decimals,DType.METADATA,'decimals()', 'uint', ['decimals','decimal']),
    (VarLabel._totalSupply,DType.TOTALSUPPLY,'totalSupply()', 'uint', ['totalsupply','supply']),
    (VarLabel._balances,DType.ASSET,'balanceOf(address)', 'mapping(address => uint256)', ['balances','balance']),
    (VarLabel._allowances,DType.ASSET,'allowance(address,address)','mapping(address => mapping(address => uint256))',['allowances','allowance']),
]

ERC721_STATE_VARIAVLES = [
    (VarLabel._name,DType.METADATA,'name()', 'string',  ['name']),
    (VarLabel._symbol,DType.METADATA,'symbol()', 'string',['symbol']),
    (VarLabel._owners,DType.ASSET,'ownerOf(uint256)','mapping(uint256 => address)',['owners'],), # 这个owner不是管理员 owner
    (VarLabel._balances,DType.ASSET,'balanceOf(address)','mapping(address => uint256)',['balances','balance']),
    (VarLabel._tokenApprovals,DType.ASSET,'getApproved(uint256)','mapping(address => uint256)',['tokenapprovals','tokenapproval']),
    (VarLabel._operatorApprovals,DType.ASSET,'isApprovedForAll(address, address)','mapping(address => mapping(address => bool))',['operatorapprovals','operatorapproval']),
    (VarLabel._uri,DType.METADATA,'tokenURI(uint256)','string',['baseuri','uri']),
    (VarLabel._uri,DType.METADATA,'baseURI()','string',['baseuri','uri'])
]

ERC1155_STATE_VARIAVLES = [
    (VarLabel._balances,DType.ASSET,'balanceOf(address, uint256)','mapping(uint256 => mapping(address => uint256))',['balances','balance']),
    (VarLabel._operatorApprovals,DType.ASSET,'isApprovedForAll(address, address)','mapping(address => mapping(address => bool))',['_operatorapprovals','operatorapproval']),
    (VarLabel._uri,DType.METADATA,'uri(uint256)','string',['uri']),
    (VarLabel._totalSupply,DType.TOTALSUPPLY,'totalSupply()', 'mapping(uint256 => uint256)', ['totalsupply','supply'])
]



'''
exclude_stateVaribles = [
    # type,name
    ('bytes16','_HEX_SYMBOLS')
]
'''

'''
    首先检测是否继承了ERC20或者ERC721或者ERC1155
    然后检测 getter 方法
    最后检测参数名称和值
'''
def _detect_inheritance(self,token,ERC_METADATA):
    if not any(
        c
        for c in self.contract.inheritance
        if c.name == token or c.name == token + 'Upgradeable'
    ):
        return
    for em in ERC_METADATA:
        for svar in self.all_state_vars:
            if svar.name == em[0].name and str(svar.type).startswith(em[3]):
                self.update_svarn_label(svar,em[0],em[1],DMethod.INHERITANCE)
                break

def _detect_getter(self,ERC_METADATA):

    for em in ERC_METADATA:
 
        #return_funs = [f for f in self.functions if f.function.full_name == em[2]]
        return_funs = [f for f in self.functions if str(f.function.full_name).lower().replace('_','') == em[2].lower()]
        if len(return_funs) == 0 : continue
        for return_fun in return_funs:
            #print(return_fun.return_var_group)
            svars = return_fun.return_var_group.state_vars
            if len(svars) == 0: continue
            if len(svars) == 1:
                #_set_state_vars_label(self,svars,em[0],em[1],DMethod.GETTER)
                self.update_svarn_label(svars[0],em[0],em[1],DMethod.GETTER,return_fun.return_var_group.callers)
                continue

            match_name = [svar for svar in svars if svar.name.lower().replace('_','') in em[4]]
            if len(match_name) == 1:
                self.update_svarn_label(match_name[0],em[0],em[1],DMethod.GETTER,return_fun.return_var_group.callers)
                continue
            
            match_type = [svar for svar in svars if str(svar.type).startswith(em[3])]
            if len(match_type) == 1:
                self.update_svarn_label(match_type[0],em[0],em[1],DMethod.GETTER,return_fun.return_var_group.callers)
                continue


from slither.slithir.operations import LibraryCall
def _detect_VS(self):
    '''
    1. totalSupply 是否为加法运算： + 或 maths.add() 运算
    2. 是否被 require(totalsupply < uint) 限制
    '''
    for svar in self.get_svars_by_label(VarLabel._totalSupply):
        if self.svarn_pool[svar].rw[3] != 1: continue
        # owner 保护的 totalSupply 写函数
        written_functions = self.svar_written_functions(svar) # totalSupply = totalSupply + amount
        read_functions = self.state_var_read_functions_dict[svar] # totalSupply.add(amount)

        for f in list(set(written_functions + read_functions) & set(self.owner_in_condition_functions)): # owner 函数
            for n in f.function.nodes:
                sn = str(n.expression)
                if not 'require' in sn and str(svar.name) in sn and ('+' in sn or '.add(' in sn):
                    if not _totalSupply_limited(self,f.require_conditions, f.if_conditions,svar):
                        self.update_svarn_label(svar,VarLabel._totalSupply,DType.VULNERABLE_SCARCITY,DMethod.DEPENDENCY)
                        return



def _totalSupply_limited(self,require_conditions,if_conditions, total_supply):
    '''
    从以下方面判断约束： 
        如果 require 依赖一个 local variable，那么跳过, 
        如果 require 中存在一个 bool 变量，则需要检测 bool 变量的写函数个数 > 1 则跳过
        如果 require 中存在其他变量，则需要检测 uint 变量的写函数个数 > 0 则跳过
    '''
    # 先检测是否存在 if (totalSupply < uint)
    for n in if_conditions:
        if total_supply in n.dep_vars_groups.state_vars:
            for svar in n.dep_vars_groups.state_vars:
                if svar != total_supply and str(svar.type).startswith('uint') and len(self.svar_written_functions(svar)) == 0: return True

    for n in require_conditions:
        #if n.dep_vars_groups.local_vars != []: continue
        for svar in n.dep_vars_groups.state_vars:
            if str(svar.type) == 'bool' and  len(self.svar_written_functions(svar)) == 1: return True
        
        for svar in n.dep_vars_groups.state_vars:
            if svar != total_supply and str(svar.type).startswith('uint') and len(self.svar_written_functions(svar)) == 0: return True
    return False


def _safeMath_add(irs,total_supply):
    for ir in irs:
        if isinstance(ir,LibraryCall) and ir.function_name == 'add':
            svar_args = [svar for svar in ir.arguments if isinstance(svar, StateIRVariable)]
            for arg in svar_args:
                if arg._non_ssa_version == total_supply:
                    return True
    return False


def _detect_name(self,ERC_METADATA):
    no_label_svars = self.get_svars_by_label()
    for em in ERC_METADATA:
        if self.get_svars_by_label(em[0]):
            continue
        match_name = [svar for svar in no_label_svars if svar.name.lower().replace('_','') in em[4]]
        if len(match_name) == 1:
            self.update_svarn_label(match_name[0],em[0],em[1],DMethod.NAME)
            continue
        match_name_type = [svar for svar in match_name if str(svar.type).startswith(em[3])]
        if len(match_name_type) == 1:
            self.update_svarn_label(match_name_type[0],em[0],em[1],DMethod.NAME)
            continue

class ERCMetadata(AbstractDetector):
    def __init__(self,naga,cn) -> None:
        super().__init__(naga,cn)
        erc = cn.erc
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
        _detect_inheritance(self.cn,self.token,self.ERC_METADATA)
        _detect_getter(self.cn,self.ERC_METADATA)
        _detect_name(self.cn,self.ERC_METADATA)
        _detect_VS(self.cn)
        _update_svar(self.cn)

    def summary(self):
        return {'MM':{}}

def _update_svar(self):
    metadata = self.get_svars_by_dtype(DType.METADATA)
    for svar in metadata:
        if self.svarn_pool[svar].rw[3] == 1:
            self.svarn_pool[svar].dType = DType.MUTABLE_METADATA