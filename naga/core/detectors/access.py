
from slither.core.variables.state_variable import StateVariable
from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.mapping_type import MappingType
from .detector_base import (_set_state_vars_label,_get_no_label_svars,_get_label_svars)
'''
Detect owner, blackList, whiteList, paused
'''

openzeppelin_contracts = [
    #'Label', 'Contract Name', 'StateVar Type', 'State Variable', 
    ('role','AccessControl','mapping(bytes32 => RoleData)','_roles'),
    ('role','AccessControl','mapping(bytes32 => AccessControl.RoleData)','_roles'),
    ('role','AccessControlEnumerable','mapping(bytes32 => EnumerableSet.AddressSet)','_roleMembers'),
    ('role','IAccessControl','mapping(bytes32 => RoleData)',None),
    ('role','IAccessControl','mapping(bytes32 => AccessControl.RoleData)',None),
    ('role','IAccessControlEnumerable','mapping(bytes32 => EnumerableSet.AddressSet)',None),
    ('owner','Ownable','address','_owner'),

    ('role','AccessControlUpgradeable','mapping(bytes32 => RoleData)','_roles'),
    ('role','AccessControlUpgradeable','mapping(bytes32 => AccessControlUpgradeable.RoleData)','_roles'),
    ('role','AccessControlEnumerableUpgradeable','mapping(bytes32 => EnumerableSetUpgradeable.AddressSet)','_roleMembers'),
    ('role','IAccessControlUpgradeable','mapping(bytes32 => RoleData)',None),
    ('role','IAccessControlUpgradeable','mapping(bytes32 => AccessControlUpgradeable.RoleData)',None),
    ('role','IAccessControlEnumerableUpgradeable','mapping(bytes32 => EnumerableSetUpgradeable.AddressSet)',None),
    ('owner','OwnableUpgradeable','address','_owner'),

    ('paused','Pausable','bool','_paused'),
    ('paused','PausableUpgradeable','bool','_paused'),

    # 0.5.0
    ('role','CapperRole','Roles.Role','_cappers'),
    ('role','MinterRole','Roles.Role','_minters'),
    ('role','PauserRole','Roles.Role','_pausers'),
    ('role','SignerRole','Roles.Role','_signers'),
    ('role','WhitelistAdminRole','Roles.Role','_whitelistAdmins'),
    ('bwList','WhitelistedRole','Roles.Role','_whitelisteds'),
]

def _detect_special_inheritance(self):
    '''
    检测是否继承了 openzeppelin 中的 contract
    '''
    self.inheritance = self.contract.inheritance
    self.inheritance_detected_svars = dict() # 记录 inheritance 方法检测出的变量
    for label in set(oz[0] for oz in openzeppelin_contracts):
        self.inheritance_detected_svars[label] = []

    oz_inheritance = [
        oz_contract
        for c in self.inheritance
            for oz_contract in openzeppelin_contracts
                if c.name == oz_contract[1]
    ]
    # 检测是否存在 openzeppelin_contracts 中的变量
    for oz in oz_inheritance:
        #print('[*] Detecting {}'.format(oz[1]), oz[2], oz[3])
        for sv in self.all_state_vars:
            #print('[*] Checking {},{}'.format(sv.name, str(sv.type)))
            if str(sv.type) == oz[2]:
                #print('[*] Found {}'.format(sv.name))
                if sv.name == oz[3] or oz[3] is None:
                    _set_state_vars_label(self,oz[0],[sv])
                    self.inheritance_detected_svars[oz[0]].append(sv)
                    break

def _is_owner_type(svar):
    if svar.type == ElementaryType('address') or svar.type == ElementaryType('bytes32'):
        return True
    elif isinstance(svar.type, MappingType) and (svar.type.type_from == ElementaryType('address') or svar.type.type_from == ElementaryType('bytes32')):
        return True

def _detect_owner_modifiers(self):
    '''
    modifier 可以找出定义的 owner, 但是这个 owner 有可能并没有被使用（例如mainnet/0x992a8a9f4bde0fb2ee1f5bbb3cb7b1e64748e13d）
    '''
    # 查找所有 onlyOwner
    all_onlyOwner_svars = []
    all_onlyRole_svars = []

    self.onlyOwner_modifiers = []
    self.onlyRole_modifiers = []
    for  m in self.contract.modifiers:
        if 'onlyowner' in str(m.name).lower():
            all_onlyOwner_svars+=m.all_state_variables_read()
            self.onlyOwner_modifiers.append(m)
        if  'onlyrole' in str(m.name).lower():
            all_onlyRole_svars+=m.all_state_variables_read()
            self.onlyRole_modifiers.append(m)

    self.all_only_modifier_svars = list(set(all_onlyOwner_svars + all_onlyRole_svars))
    self.only_modifiers_detected_owners = []

    for svar in all_onlyOwner_svars:
        if not _is_owner_type(svar):
            continue
        _set_state_vars_label(self,'owner',[svar])
        self.only_modifiers_detected_owners.append(svar)
    for svar in all_onlyRole_svars:
        if not _is_owner_type(svar):
            continue
        _set_state_vars_label(self,'role',[svar])
        self.only_modifiers_detected_owners.append(svar)

from slither.core.declarations import SolidityVariableComposed

def _is_owner(svar,owners,written_functions):
    t_owners = [svar] + owners
    for f in written_functions:
        if f.is_constructor_or_initializer: continue
        # 如果存在一个 condition 读取了 owners 和 msg.sender
        if any(
            SolidityVariableComposed('msg.sender') in cond.all_read_vars_group.solidity_vars 
            and set(cond.all_read_vars_group.state_vars) & set(t_owners) != set()
            for cond in f.conditions
        ):
            continue
        return False # 否则返回 False
    return True

def detect_owners(self):
    # 先搜索继承 和 modifier 中的 owner
    _detect_special_inheritance(self)
    _detect_owner_modifiers(self)

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
    owner_candidates = _get_no_label_svars(self,list(set(owner_candidates)))
    #for v in owner_candidates: print('[*] Detecting owner of {}'.format(v.name))
    '''
     查找 owner, 如果 candidate 的写函数不是 constructor，则需要存在一个require，其中读取了 变量自己 或 另一个 owner ，并且读取了 msg.sender
    '''
    owners = _get_label_svars(self,'owner') + _get_label_svars(self,'role')
    max_deep = (len(owner_candidates) + 1) * len(owner_candidates) / 2 + 1 # 最差情况下，每个owner 都互相依赖，且我们每次只能检出一个 owner
    now_deep = 0
    while len(owner_candidates) > 0 and now_deep <= max_deep:
        now_deep += 1
        svar = owner_candidates.pop(0)
        #print('[{}] Detecting owner of {}'.format(now_deep,svar.name))
        if _is_owner(svar,owners,self.state_var_written_functions_dict[svar]):
            _set_state_vars_label(self,'owner',[svar])
            owners.append(svar)
        owner_candidates.append(svar)

    _detect_bwList(self)
    _after_detect_owners(self)

def _detect_bwList(self):
    '''
    检查 mapping 类型的 owner 是否是黑名单
    blackList / whiteList 和 admin 有相同的模式，因此，需要排除 blackList / whiteList
    具体而言，我们检查 token_written_functions 中出现的 owner: mapping，如果存在，我们认为它是 blackList / whiteList 而不是 owner
    '''
    owners = _get_label_svars(self,'owner') + _get_label_svars(self,'role')
    mapping_owners = [svar for svar in owners if isinstance(svar.type, MappingType)]
    twf_conditions = [cond for f in self.token_written_functions for cond in f.conditions]

    for svar in mapping_owners:
        # 如果 svar 在任意一个 token_written_functions 的 condition 中被读，则认为它是 blackList / whiteList，不是 owner
        if any(
            SolidityVariableComposed('msg.sender') in cond.all_read_vars_group.solidity_vars 
            and svar in cond.all_read_vars_group.state_vars
            for cond in twf_conditions
        ):
            _set_state_vars_label(self,'bwList',[svar])

def _after_detect_owners(self):
    owner_in_condition_functions = []

    for svar in _get_label_svars(self,'owner') + _get_label_svars(self,'role'):
        owner_in_condition_functions += self.state_var_read_in_condition_functions_dict[svar]

    self.owner_in_condition_functions = list(set(owner_in_condition_functions))


def access_printer(self):
    pass

