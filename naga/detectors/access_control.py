from .abstract_detector import *
from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.mapping_type import MappingType

class AccessControl(AbstractDetector):
    def _detect(self):
        _detect_owners(self.cn)
        _detect_blacklist(self.cn)
        _multistage_owners(self.cn)
        _set_owner_in_condition_functions(self.cn)
        _divde_state_vars(self.cn)

    def summary(self):

        return{
            'AC':{
                
            }
        }


openzeppelin_contracts = [
    #'Label', 'Contract Name', 'StateVar Type', 'State Variable', 
    (VarLabel.role, DType.ACCESS_CONTROL,'AccessControl','mapping(bytes32 => RoleData)','_roles'),
    (VarLabel.role, DType.ACCESS_CONTROL,'AccessControl','mapping(bytes32 => AccessControl.RoleData)','_roles'),
    (VarLabel.role, DType.ACCESS_CONTROL,'AccessControlEnumerable','mapping(bytes32 => EnumerableSet.AddressSet)','_roleMembers'),
    #(VarLabel.role, DType.ACCESS_CONTROL,'IAccessControl','mapping(bytes32 => RoleData)','_roles'),#
    #(VarLabel.role, DType.ACCESS_CONTROL,'IAccessControl','mapping(bytes32 => AccessControl.RoleData)','_roles'), #
    #(VarLabel.role, DType.ACCESS_CONTROL,'IAccessControlEnumerable','mapping(bytes32 => EnumerableSet.AddressSet)','_roleMembers'),#
    (VarLabel.owner,DType.ACCESS_CONTROL,'Ownable','address','_owner'),

    (VarLabel.role, DType.ACCESS_CONTROL,'AccessControlUpgradeable','mapping(bytes32 => RoleData)','_roles'),
    (VarLabel.role, DType.ACCESS_CONTROL,'AccessControlUpgradeable','mapping(bytes32 => AccessControlUpgradeable.RoleData)','_roles'),
    (VarLabel.role, DType.ACCESS_CONTROL,'AccessControlEnumerableUpgradeable','mapping(bytes32 => EnumerableSetUpgradeable.AddressSet)','_roleMembers'),
    #(VarLabel.role, DType.ACCESS_CONTROL,'IAccessControlUpgradeable','mapping(bytes32 => RoleData)','_roles'), #
    #(VarLabel.role, DType.ACCESS_CONTROL,'IAccessControlUpgradeable','mapping(bytes32 => AccessControlUpgradeable.RoleData)','_roles'), #
    #(VarLabel.role, DType.ACCESS_CONTROL,'IAccessControlEnumerableUpgradeable','mapping(bytes32 => EnumerableSetUpgradeable.AddressSet)','_roleMembers'),#
    (VarLabel.owner,DType.ACCESS_CONTROL,'OwnableUpgradeable','address','_owner'),

    (VarLabel.paused,DType.LIMITED_LIQUIDITY,'Pausable','bool','_paused'),
    (VarLabel.paused,DType.LIMITED_LIQUIDITY,'PausableUpgradeable','bool','_paused'),

    # 0.5.0
    #(VarLabel.role, DType.ACCESS_CONTROL,'CapperRole','Roles.Role','_cappers'),
    #(VarLabel.role, DType.ACCESS_CONTROL,'MinterRole','Roles.Role','_minters'),
    #(VarLabel.role, DType.ACCESS_CONTROL,'PauserRole','Roles.Role','_pausers'),
    #(VarLabel.role, DType.ACCESS_CONTROL,'SignerRole','Roles.Role','_signers'),
    #(VarLabel.role, DType.ACCESS_CONTROL,'WhitelistAdminRole','Roles.Role','_whitelistAdmins'),
    #('whitelist','WhitelistedRole','Roles.Role','_whitelisteds'),
]


def __detect_inheritance(self):
    '''
    检测是否继承了 openzeppelin 中的 contract
    '''
    self.inheritance = self.contract.inheritance

    oz_inheritance = [
        oz_contract
        for c in self.inheritance
            for oz_contract in openzeppelin_contracts
                if c.name == oz_contract[2]
    ]
    # 检测是否存在 openzeppelin_contracts 中的变量
    for oz in oz_inheritance:
        for svar in self.all_state_vars:
            if str(svar.type) == oz[3]:
                if svar.name == oz[4]:
                    self.update_svarn_label(svar,oz[0],oz[1],DMethod.INHERITANCE)
                    break

openzeppelin_modifiers = [
    (VarLabel.owner,DType.ACCESS_CONTROL,'onlyowner',['address','byte32']),
    (VarLabel.role, DType.ACCESS_CONTROL,'onlyrole',['address','byte32']),
    (VarLabel.paused,DType.LIMITED_LIQUIDITY,'whennotpaused',['bool']),
    (VarLabel.paused,DType.LIMITED_LIQUIDITY,'whenpaused',['bool'])
    ]

'''
def _startswith(ss,prefixs):
    for prefix in prefixs:
        if ss.startswith(prefix):
            return True
    return False
'''

def __detect_modifiers(self):
    '''
    modifier 可以找出定义的 owner, 但是这个 owner 有可能并没有被使用（例如mainnet/0x992a8a9f4bde0fb2ee1f5bbb3cb7b1e64748e13d）
    '''
    self.modifier_dict = {}
    self.modifier_dict[DType.ACCESS_CONTROL] = []
    self.modifier_dict[DType.LIMITED_LIQUIDITY] = []
    
    for m in self.contract.modifiers:
        for om in openzeppelin_modifiers:
            if str(m.name).lower().replace('_','') == om[2]:
                svars = m.all_state_variables_read()
                if len(svars) == 1:
                    self.update_svarn_label(svars[0],om[0],om[1],DMethod.MODIFIER)
                    self.modifier_dict[om[1]].append(m)
                else:
                    for svar in svars:
                        if str(svar.type) in om[3]:
                            self.update_svarn_label(svar,om[0],om[1],DMethod.MODIFIER)
                            self.modifier_dict[om[1]].append(m)
                break

    self.modifier_dict[DType.ACCESS_CONTROL] = list(set(self.modifier_dict[DType.ACCESS_CONTROL]))
    self.modifier_dict[DType.LIMITED_LIQUIDITY] = list(set(self.modifier_dict[DType.LIMITED_LIQUIDITY]))

from slither.core.declarations import SolidityVariableComposed

def _is_owner(svar,owners,written_functions):
    t_owners = [svar] + owners
    for f in written_functions:
        if f.is_constructor_or_initializer: continue
        # 如果存在一个 condition 读取了 owners 和 msg.sender
        if any(
            SolidityVariableComposed('msg.sender') in cond.dep_vars_groups.solidity_vars 
            and set(cond.dep_vars_groups.state_vars) & set(t_owners) != set()
            for cond in f.conditions
        ):
            continue
        return False # 否则返回 False
    return True

def _is_written_by_other_owner(svar,owners,written_functions):
    '''
    校验一个变量是否被其他 owner 写入
    '''
    t_owners = list(set(owners)- set([svar]))
    for f in written_functions:
        if f.is_constructor_or_initializer: continue
        # 如果存在一个 condition 读取了 owners 和 msg.sender
        if any(
            SolidityVariableComposed('msg.sender') in cond.dep_vars_groups.solidity_vars 
            and set(cond.dep_vars_groups.state_vars) & set(t_owners) != set()
            for cond in f.conditions
        ):
            continue
        return False # 否则返回 False
    return True

def _detect_blacklist(self):
    '''
    检查 bwList 可能和 owner 有相同的模式，也可能接收外部变量
    例如：
        require(!_blacklist[msg.sender]);
        require(!_blacklist[sender] && !_blacklist[recipient], "Blacklisted!");
    因此我们检查所有的 mapping(address => bool) 类型变量，如果它的写依赖于 owner(不能是自己)，且出现在 token_written_functions 的 require 中 则认为是 bwList
    '''
    owners = self.get_svars_by_dtype(DType.ACCESS_CONTROL)
    blacklist_candidates = [svar for svar in self.all_state_vars if isinstance(svar.type, MappingType) and svar.type.type_from == ElementaryType('address') and svar.type.type_to == ElementaryType('bool')]

    twf_conditions = [cond for f in self.token_written_functions for cond in f.conditions]
    for svar in blacklist_candidates:
        if not _is_written_by_other_owner(svar,owners,self.state_var_written_functions_dict[svar]):
            continue
        if any(
            svar in cond.dep_vars_groups.state_vars
            for cond in twf_conditions
        ): # 如果出现在 token_written_functions 中，注意，这里并没有校验 msg.sender # SolidityVariableComposed('msg.sender') in cond.dep_vars_groups.solidity_vars 
            self.update_svarn_label(svar,VarLabel.blacklist,DType.LIMITED_LIQUIDITY,DMethod.DEPENDENCY)

def _set_owner_in_condition_functions(self):

    owner_in_condition_functions = []
    access_modifiers = self.modifier_dict[DType.ACCESS_CONTROL]

    for f in self.functions:
        if set(f.function.modifiers) & set(access_modifiers) != set():
            owner_in_condition_functions.append(f)

    for svar in self.get_svars_by_dtype(DType.ACCESS_CONTROL):
        owner_in_condition_functions += self.state_var_read_in_condition_functions_dict[svar]
    self.owner_in_condition_functions = list(set(owner_in_condition_functions))

def _multistage_owners(self):
    multistage_owners = self.get_svars_by_label(VarLabel.role)
    for owner in self.get_svars_by_label(VarLabel.owner):
        if _is_owner(owner,[owner],self.state_var_written_functions_dict[owner]): # 如果更新 owner 只依赖自己，则不是 multistage owner
            continue
        multistage_owners.append(owner)
    self.multistage_owners = multistage_owners

def _detect_owners(self):
    # 先搜索继承 和 modifier 中的 owner
    __detect_inheritance(self)
    __detect_modifiers(self)

    """
    1. owner 需要是 state variable
    2. owner 的类型是 address 或 mapping()
    3. owner 如果存在写函数，
        3.1 为构造函数
     或 3.2 写函数被自己或另一个 owner 约束

    简单来说，如果一个变量是 owner,除 constructor 外，限制仅被自己或另一个 owner 写入
    """

    # 检索所有的 function 查看是否有符合类型的 state variable
    #conditions = [cond for f in self.functions for cond in f.conditions]

    owner_candidates = [svar for f in self.functions for svar in f.owner_candidates]
    #for c in all_candidates: print(c)
    # 去掉 inheritance 和 modifier 中检测到的 owner
    owner_candidates = list(set(self.get_svars_by_label()) & set(owner_candidates)) 
    #for v in owner_candidates: print('[*] Detecting owner of {}'.format(v.name))
    '''
     查找 owner, 如果 candidate 的写函数不是 constructor，则需要存在一个require，其中读取了 变量自己 或 另一个 owner ，并且读取了 msg.sender
    '''
    owners = self.get_svars_by_dtype(DType.ACCESS_CONTROL)
    max_deep = (len(owner_candidates) + 1) * len(owner_candidates) / 2 + 1 # 最差情况下，每个owner 都互相依赖，且我们每次只能检出一个 owner
    now_deep = 0
    while len(owner_candidates) > 0 and now_deep <= max_deep:
        now_deep += 1
        svar = owner_candidates.pop(0)
        #print('[{}] Detecting owner of {}'.format(now_deep,svar.name))
        if _is_owner(svar,owners,self.state_var_written_functions_dict[svar]):
            self.update_svarn_label(svar,VarLabel.owner,DType.ACCESS_CONTROL,DMethod.DEPENDENCY)
            owners.append(svar)
        owner_candidates.append(svar)

def _divde_state_vars(self):
    '''
    在 owner 检测结束后，将 state_vars 划分为 user 和 owner 两部分
    '''

    svars_read = []
    svars_user_read = []
    svars_owner_read = []

    svars_written = []
    svars_user_written = []
    svars_owner_updated = []

    svars_user_only_read = [] # self.svars_user_read - self.svars_user_written
    svars_user_only_read_owner_updated = [] #self.svars_user_only_read & self.svars_owner_updated
    svars_user_written_owner_updated = []

    for f in self.state_var_read_functions:
        svars = f.function.all_state_variables_read()
        svars_read += svars
        if f.is_constructor_or_initializer: continue
        if f in self.owner_in_condition_functions: svars_owner_read += svars
        else: svars_user_read += svars
    svars_read = list(set(svars_read))
    svars_user_read = list(set(svars_user_read))
    svars_owner_read = list(set(svars_owner_read))

    for f in self.state_var_written_functions:
        svars = f.function.all_state_variables_written()
        svars_written += svars
        if f.is_constructor_or_initializer: continue
        if f in self.owner_in_condition_functions: svars_owner_updated += svars
        else: svars_user_written += svars
    svars_written = list(set(svars_written))
    svars_user_written = list(set(svars_user_written))
    svars_owner_updated = list(set(svars_owner_updated))

    svars_user_only_read = list(set(svars_user_read)-set(svars_user_written))
    svars_user_only_read_owner_updated = list(set(svars_user_only_read) & set(svars_owner_updated))
    svars_user_written_owner_updated = list(set(svars_user_written) & set(svars_owner_updated))

    self.state_vars_read = svars_read
    self.state_vars_owner_read =svars_owner_read
    self.state_vars_user_read = svars_user_read

    self.state_vars_written = svars_written
    self.state_vars_user_written = svars_user_written
    self.state_vars_owner_updated = svars_owner_updated

    self.state_vars_user_only_read = svars_user_only_read
    self.state_vars_user_only_read_owner_updated = svars_user_only_read_owner_updated
    self.state_vars_user_written_owner_updated = svars_user_written_owner_updated
