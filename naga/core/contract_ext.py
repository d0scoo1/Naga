
from typing import List, Dict, Tuple
from xml.dom.minidom import Identified
from slither.core.declarations import Contract
from slither.core.variables.state_variable import StateVariable

from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.mapping_type import MappingType

from .function_ext import FunctionEXT
from .require_ext import RequireEXT
from .state_variable_ext import (StateVarType,StateVariableEXT)
from .erc import (ERC20_WRITE_FUNCS_SIG,ERC721_WRITE_FUNCS_SIG,ERC1155_WRITE_FUNCS_SIG)

# TODO: Non-Unique Identification
# TODO: Unfair Setting
# TODO: Unknow Risk

class ContractEXT():
    def __init__(self,contract: Contract):
        self.contract = contract
        self.functions: List["FunctionEXT"] = None # 所有的 entry function
        # Function 
        
        self.state_var_written_functions: List["FunctionEXT"] = None
        self.state_var_read_functions: List["FunctionEXT"] = None
        self.state_var_written_functions_dict:Dict(str(StateVariable),["FunctionEXT"]) = None
        self.state_var_read_functions_dict:Dict(str(StateVariable),["FunctionEXT"]) = None
        self.state_var_read_in_require_functions_dict: List["FunctionEXT"] = None
        self.state_var_read_in_requires_dict: Dict(str(StateVariable),["RequireEXT"]) = None
        self.all_state_vars: List[StateVariable] = None

        self.token_write_function_sigs = list(set(ERC20_WRITE_FUNCS_SIG+ERC721_WRITE_FUNCS_SIG+ERC1155_WRITE_FUNCS_SIG))
        #["transfer(address,uint256)", "transferFrom(address,address,uint256)","approve(address,uint256)","allowance(address,address)","setApprovalForAll(address,bool)","safeTransferFrom(address,address,uint256,uint256,bytes)","safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)"]
        self.token_written_functions: List["FunctionEXT"] = None # 接口中定义的用户的写函数，我们通过这些函数来判定一个 owner 是否为 bwList 或 paused

        self._dividing_functions()

        # Owner & BW List
        self.owners: List["StateVariable"] = []
        self.bwList: List["StateVariable"] = []
        self._search_owners_bwList()
        self._update_function_owners()

        # Event
        self.lack_event_functions: List["FunctionEXT"] = []
        self.lack_event_functions_owner: List["FunctionEXT"] = [] # owner 写的 function 缺少 event
        self.lack_event_functions_user: List["FunctionEXT"] = [] # user 写的 function 缺少 event
        self._serach_lack_event_functions()

        # State Variable
        self.all_ext_state_vars: List[StateVariableEXT] = None
        self.ext_state_vars_dict: Dict(StateVariable,StateVariableEXT) = None

        self.state_var_exts_read = []
        self.state_var_exts_owner_read = []
        self.state_var_exts_user_read = []

        self.state_var_exts_written = []
        self.state_var_exts_user_written = []
        self.state_var_exts_owner_updated = [] # 这里使用 updated 而不是 written 是因为，构造函数中，由 owner written 了一些变量， updated 表示不包括构造函数。

        self.state_var_exts_user_only_read = []
        self.state_var_exts_user_only_read_owner_updated = []
        self.state_var_exts_user_written_owner_updated = []
        self._divding_ext_state_variables()
        self._search_ext_state_variables()


        

        #self.paused = self._search_paused()
        #self.totalSupply = self._search_totalSupply()
        #self.balances = self._search_balances()
        #self.allowed = self._search_allowed()
        #self.identifies = self._search_identifies()
        #self.unfair_settings = self._get_unfair_settings() # 其他 owner 可以设置的变量


    def _dividing_functions(self):
        """
            初始化所有相关的 function
        """

        self.functions = []
        self.state_var_written_functions = []
        self.state_var_read_functions = []
        for f in self.contract.functions_entry_points: # functions_declared():
            f = FunctionEXT(f)
            self.functions.append(f)
            if len(f.function.all_state_variables_read()) > 0:
                self.state_var_read_functions.append(f)
            if len(f.function.all_state_variables_written()) > 0:
                self.state_var_written_functions.append(f)
        
        
        # 获取所有的 transfer functions
        self.token_written_functions = []
        for fs in self.token_write_function_sigs :
            f = self.get_function_from_signature(fs)
            if f is not None:
                self.token_written_functions.append(f)
        

        # 获取所有的 state variables
        self.state_var_written_functions_dict = dict()
        self.state_var_read_functions_dict = dict()
        self.state_var_read_in_require_functions_dict = dict()
        self.state_var_read_in_requires_dict = dict()

        #for svar in self.contract.state_variables: # self.contract.state_variables 是不完整的
        #    all_state_vars.append(svar)
            #print(svar,type(svar),hex(id(svar)))
        
        all_state_vars = []
        for f in self.functions:
            for svar in f.function.all_state_variables_written() + f.function.all_state_variables_read():
                all_state_vars.append(svar)
            for exp_req in f.requires:
                for svar in exp_req.all_read_vars_group.state_vars:
                    all_state_vars.append(svar)
    
        self.all_state_vars = list(set(all_state_vars))
        for s in self.all_state_vars:
            self.state_var_written_functions_dict[s] = []
            self.state_var_read_functions_dict[s] = []
            self.state_var_read_in_requires_dict[s] = []
            self.state_var_read_in_require_functions_dict[s] = []

        for f in self.functions:
            for svar in f.function.all_state_variables_written():
                self.state_var_written_functions_dict[svar].append(f)
            for svar in f.function.all_state_variables_read():
                self.state_var_read_functions_dict[svar].append(f)

            for exp_req in f.requires:
                #print(exp_req)
                for svar in exp_req.all_read_vars_group.state_vars:
                    self.state_var_read_in_requires_dict[svar].append(exp_req)
                    self.state_var_read_in_require_functions_dict[svar].append(f)
            
            for svar, value in self.state_var_read_in_require_functions_dict.items():
                self.state_var_read_in_require_functions_dict[svar] = list(set(value))


    def get_function_from_signature(self, function_signature):
        """
            获取 public / external 函数
        """
        return next(
            (FunctionEXT(f) for f in self.contract.functions if f.full_name == function_signature and not f.is_shadowed),
            None,
        )

    def get_written_functions(self,state_var) -> List[FunctionEXT]:
        return [f for f in self.functions if state_var in f.function.all_state_variables_written()]


    def _search_owners_bwList(self):
        """
            搜索所有的 owners
            1. owner 需要是 state variable
            2. owner 的类型是 address 或 mapping()
            3. owner 如果存在写函数，
                3.1 为构造函数
            或 3.2 写函数被 require约束，且约束条件中仅包含 state var, msg.sender
        """

        # 检索所有的 function 查看是否有符合类型的 state variable
        owner_candidates = []
        for f in self.functions:
            #print('--',f.function.full_name,f.state_vars_read_in_requires)
            for svar in f.owner_candidates:
                # 检查 candidates 所有的写函数是否被 owner 约束
                # 如果不是构造函数，并且不存在 owner candidates
                if any(len(f2.owner_candidates) == 0 and not f2.function.is_constructor
                    for f2 in self.state_var_written_functions_dict[svar]
                    ):
                    continue
                # 否则，增加到 owner_candidates
                owner_candidates.append(svar)

        # 检查每个 owner_candidate 依赖的 owner 是否也属于 owner_candidate
        # 首先找出自我依赖的，然后检查剩余的是否依赖于自我依赖
        owners = []
        for svar in owner_candidates:
            # 检查是否存在自我依赖：owner 的写函数是 owner in require functions 的子集 (上一步中，我们已经确定每个 owner 的写函数都被 owner_candidates 约束)

            read_in_require_funcs = self.state_var_read_in_require_functions_dict[svar]
            # 去掉 written_funcs 中的构造函数
            written_funcs =[f for f in self.state_var_written_functions_dict[svar] if not f.function.is_constructor]

            if len(set(written_funcs) - set(read_in_require_funcs)) > 0:
                continue
            owners.append(svar)
        
        # 检查剩余的 owner 是否依赖于 owner
        # 找出每个 candidates 的写函数，得到他们写函数的约束的 owner,如果约束 owner 存在于上述 owner 中，则成立，
        owners = list(set(owners))
        owner_candidates = list(set(owner_candidates)-set(owners))
        
        for svar in owner_candidates:
            dep_owners = []
            for t_wf in self.state_var_written_functions_dict[svar]: dep_owners += t_wf.owner_candidates # 这里 构造函数不存在 owners，因此不用管
            if len(set(owners) - set(dep_owners)) == 0:
                owners.append(svar)

        # 如果有 mapping，则需要检查是否为 bwList
        mapping_owners = []
        for svar in owners:
            if isinstance(svar.type, MappingType):
                mapping_owners.append(svar)
        if len(mapping_owners) == 0:
            self.owners = owners
            return

        # blackList / whiteList 和 admin 有相同的模式，因此，需要排除 blackList / whiteList
        # 具体而言，我们检查 token_written_functions 中出现的 mapping owner candidates，如果和 owners 中匹配，我们认为它是 blackList / whiteList 而不是 owner
        bwList = []

        for ef in self.token_written_functions:
            for svar in ef.owner_candidates:
                #if isinstance(svar.type, MappingType) and svar.type.type_from == ElementaryType('address') and svar.type.type_to == ElementaryType('bool'):
                if svar in mapping_owners:
                    bwList.append(svar)

        self.owners = list(set(owners)-set(bwList))
        self.bwList = list(set(bwList))

    def _update_function_owners(self):
        """
            更新所有的 function 的 owner
        """
        for svar in self.owners:
            for f in self.state_var_read_in_require_functions_dict[svar]:
                f.owners.append(svar)

    def _serach_lack_event_functions(self):
        """
            TODO:需要再次确认， owner 的函数是否需要 event
            如果一个 function 写了 state variable，则应当发送一个 event，提醒用户，这里寻找缺少的 event 的 function。
            我们并不考虑 event 的参数，关于 event 和实际操作不一致的问题：TokenScope: Automatically Detecting Inconsistent Behaviors of Cryptocurrency Tokens in Ethereum
        """

        for f in self.state_var_written_functions:
            if not f.function.is_constructor and len(f.events) == 0:
                if len(f.owners) == 0:
                    self.lack_event_functions_user.append(f)
                else:
                    self.lack_event_functions_owner.append(f)

        self.lack_event_functions = self.lack_event_functions_owner + self.lack_event_functions_user

    
    def _divding_ext_state_variables(self):
        """
            搜索用户调用的标准接口中所有读写的变量，如：手续费，balance，
            如果一个变量用户可以写，而owner也可以写（例如 balance），那么说明 owner 可以操纵用户数据，（潜在的风险是，owner 泄露时，黑客可以转走钱）

            如果一个变量用户不能写，但是 owner 可以写，我们认为这个变量是约束变量，例如 paused, 手续费等
            如果这些变量，owner 也可以修改，则这些变量是 unfair_settings

            用户可以写，owner 也可以写，用户不能写， owner 可以写
        """
        self.all_ext_state_vars = []
        for svar in self.owners:
            sve = StateVariableEXT(svar)
            sve.set_data(self.state_var_read_functions_dict[svar], 
                        self.state_var_written_functions_dict[svar],
                        self.state_var_read_in_require_functions_dict[svar],
                        self.state_var_read_in_requires_dict[svar])
            sve.stype = StateVarType.OWNER
            self.all_ext_state_vars.append(sve)

        for svar in self.bwList:
            sve = StateVariableEXT(svar)
            sve.set_data(self.state_var_read_functions_dict[svar], 
                        self.state_var_written_functions_dict[svar],
                        self.state_var_read_in_require_functions_dict[svar],
                        self.state_var_read_in_requires_dict[svar])
            sve.stype = StateVarType.BWLIST
            self.all_ext_state_vars.append(sve)

        for svar in list(set(self.all_state_vars)-set(self.owners)-set(self.bwList)):
            sve = StateVariableEXT(svar)
            sve.set_data(self.state_var_read_functions_dict[svar], 
                        self.state_var_written_functions_dict[svar],
                        self.state_var_read_in_require_functions_dict[svar],
                        self.state_var_read_in_requires_dict[svar])
            self.all_ext_state_vars.append(sve)
        
        self.ext_state_vars_dict = dict()
        for sve in self.all_ext_state_vars:
            self.ext_state_vars_dict[sve.svar] = sve

        state_var_exts_read = []
        state_var_exts_user_read = []
        state_var_exts_owner_read = []

        state_var_exts_written = []
        state_var_exts_user_written = []
        state_var_exts_owner_updated = []

        state_var_exts_user_only_read = [] # self.state_var_exts_user_read - self.state_var_exts_user_written
        state_var_exts_user_only_read_owner_updated = [] #self.state_var_exts_user_only_read & self.state_var_exts_owner_updated
        state_var_exts_user_written_owner_updated = []

        for svar in self.all_ext_state_vars:
            if svar.is_user_readable:
                state_var_exts_user_read.append(svar)
            if svar.is_user_writable:
                state_var_exts_user_written.append(svar)
            if svar.is_owner_readable:
                state_var_exts_owner_read.append(svar)
            if svar.is_owner_writable:
                state_var_exts_owner_updated.append(svar)
        
        state_var_exts_read = list(set(state_var_exts_user_read + state_var_exts_owner_read))
        state_var_exts_written = list(set(state_var_exts_user_written + state_var_exts_owner_updated))
        state_var_exts_user_only_read = list(set(state_var_exts_user_read) - set(state_var_exts_user_written))
        state_var_exts_user_only_read_owner_updated = list(set(state_var_exts_user_only_read) & set(state_var_exts_owner_updated))
        state_var_exts_user_written_owner_updated = list(set(state_var_exts_user_written) & set(state_var_exts_owner_updated))

        self.state_var_exts_read = state_var_exts_read
        self.state_var_exts_owner_read =state_var_exts_owner_read
        self.state_var_exts_user_read = state_var_exts_user_read

        self.state_var_exts_written = state_var_exts_written
        self.state_var_exts_user_written = state_var_exts_user_written
        self.state_var_exts_owner_updated = state_var_exts_owner_updated

        self.state_var_exts_user_only_read = state_var_exts_user_only_read
        self.state_var_exts_user_only_read_owner_updated = state_var_exts_user_only_read_owner_updated
        self.state_var_exts_user_written_owner_updated = state_var_exts_user_written_owner_updated


    def __search_one_state_var_in_return(self, f_sig, type_str, svar_lower_names):
        """ 
            查找 return 中的返回值
        """
        f = self.get_function_from_signature(f_sig)
        if f is None:
            return None

        svars = [svar for svar in f.return_var_group.state_vars if str(svar.type).startswith(type_str)]

        if len(svars) == 0:
            return None
        elif len(svars) == 1:
            return svars[0]
        else:
            for svar in svars:
                for name in svar_lower_names:
                    if name in svar.name.lower():
                        return svar

    def _search_ext_state_variables(self):
        """
            搜索所有的 paused
            paused 符合以下特点，出现在 tranfer 的 require 中（没有 local variables 出现在 require 中），bool 类型，只有 owner 可以修改
        """
        paused_candidates = []
        for sve in self.state_var_exts_user_only_read_owner_updated:
            if sve.svar.type == ElementaryType('bool'):
                paused_candidates.append(sve)
    
        for sve in list(set(paused_candidates)):
            funcs_sigs = [f.function.full_name for f in sve.read_in_require_functions]
            if len(set(funcs_sigs) & set(self.token_write_function_sigs)) > 0: # 如果变量 require function 出现在 token 写函数中
                sve.stype = StateVarType.PAUSED

        """
            查找 totalSupply 变量
        """
        totalsupply = self.__search_one_state_var_in_return('totalSupply()','uint256',['total','supply'])
        if totalsupply is not None:
            self.ext_state_vars_dict[totalsupply].stype = StateVarType.TOTAL_SUPPLY

        """
            搜索 balance 变量
        """
        balances = self.__search_one_state_var_in_return('balanceOf(address)','mapping(address => uint256)',['balance'])
        if balances is None:
            balances = self.__search_one_state_var_in_return('balanceOf(address,uint256)','mapping(uint256 => mapping(address => uint256))',['balance'])
        if balances is not None:
            self.ext_state_vars_dict[balances].stype = StateVarType.BALANCES

        """
            搜索 allowance 变量
        """
        allowance = self.__search_one_state_var_in_return('allowance(address,address)','mapping(address => mapping(address => uint256))',['allow'])
        if allowance is not None:
            self.ext_state_vars_dict[allowance].stype = StateVarType.ALLOWED
     
        """
            一个代币使用 name 和 symbol 的方式来标识自己，搜索所有的 name 和 symbol
            ERC20 是标准接口，ERC721 是可选，ERC1155 则不需要
        """
        identifies = []
        name = self.__search_one_state_var_in_return('name()','string',['name'])
        if name is not None: identifies.append(name)
        
        symbol = self.__search_one_state_var_in_return('symbol()','string',['symbol'])
        if symbol is not None: identifies.append(symbol)
        
        decimals = self.__search_one_state_var_in_return('decimals()','uint',['decimals'])
        if decimals is not None: identifies.append(decimals)

        for svar in self.state_var_exts_written:
            if svar.svar.type == ElementaryType('string') and svar.svar.name.lower() in ['name','symbol']:
                identifies.append(svar)
            elif str(svar.svar.type).startswith('uint'):
                if svar.svar.name.lower() in ['decimals']:
                    identifies.append(svar)

        for svar in list(set(identifies)):
            self.ext_state_vars_dict[svar].stype = StateVarType.IDENTIFY

    def __str__(self) -> str:
        return self.contract.name

    def summary(self):
        
        return '\ncontract:{}\nstate vars:{}\nowner:{}\nbwList:{}\nlack event functions:{}\n'.format(self.contract.name,list2str(self.all_ext_state_vars),list2str(self.owners),list2str(self.bwList),list2str(self.lack_event_functions))
        """
        return '\ncontract:{}\nstate vars:{}\nowner:{}\nbwList:{}\npaused:{}\ntotalSupply:{}\nbalances:{}\nallowed:{}\nidentifies:{}\n'\
        'Owner can update: totalSupply:{}, balances:{}, allowed:{}, identifies:{}, unfair settings:{}\nlack event functions:{}\n'.format(self.contract.name,list2str(self.all_ext_state_vars),list2str(self.owners),list2str(self.bwList),list2str(self.paused), self.totalSupply, self.balances, self.allowed, list2str(self.identifies),list2str(self.unfair_settings),self.is_owner_updated_totalSupply,self.is_owner_updated_balances,self.is_owner_updated_allowed,list2str(self.owner_updated_identifies),list2str(self.lack_event_functions))
        """
       
      

def list2str(l):
    l = [str(i) for i in l]
    return ','.join(l)
    