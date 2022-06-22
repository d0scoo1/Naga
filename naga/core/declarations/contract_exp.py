
from signal import pause
from typing import Any, Optional, List, Dict, Callable, Tuple, TYPE_CHECKING, Union
from slither.core.declarations import Contract
from slither.core.declarations import FunctionContract
#from naga.utils.token import(IERC20_FUNCTIONS_SIG,IERC721_FUNCTIONS_SIG,IERC777_FUNCTIONS_SIG, IERC1155_FUNCTIONS_SIG,)
from .function_exp import FunctionExp
from .variable_exp import VariableExp
from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.mapping_type import MappingType

# TODO: Non-Unique Identification
# TODO: Unfair Setting
# TODO: Unknow Risk

class ContractExp():
    def __init__(self,contract: Contract):
        self.contract = contract
        self.functions: List["FunctionExp"] = None # 所有的 entry function
        self.state_var_written_functions: List["FunctionExp"] = None
        self.state_var_read_functions: List["FunctionExp"] = None
        self.user_written_functions: List["FunctionExp"] = None # 所有用户写入的 functions
        #self.state_variables: List[VariableExp] = None # 所有的 state variable
        self.state_var_written_functions_dict = None
        self.state_var_read_functions_dict = None
        self.state_var_read_in_require_functions_dict = None
        self.state_var_read_require_dict = None

        self.owners = []
        self.bwList = []

        self.transfer_function_sigs = ["transfer(address,uint256)", "transferFrom(address,address,uint256)","approve(address,uint256)","allowance(address,address)"]

        self.pasued = []
        self.totalSupply = None
        self.identifies = []
        self.user_state_variables = []
        self.lack_event_functions = []

        self._init_base()
        self._search_owners_bwList()
        self._update_function_owners()

        self._search_paused()
        self._search_totalSupply()
        #self._search_identifies()
        #self._search_user_state_vars()
        #self._serach_lack_event_functions()


    def _init_base(self):
        """
            初始化所有相关的 function
        """

        self.functions = []
        self.state_var_written_functions = []
        self.state_var_read_functions = []
        for f in self.contract.functions_entry_points: # functions_declared():
            f = FunctionExp(f)
            self.functions.append(f)
            if len(f.function.all_state_variables_read()) > 0:
                self.state_var_read_functions.append(f)
            if len(f.function.all_state_variables_written()) > 0:
                self.state_var_written_functions.append(f)

        # 获取所有的 transfer functions
        
        self.user_written_functions = []
        for fs in self.transfer_function_sigs :
            f = self.get_function_from_signature(fs)
            if f is not None:
                self.user_written_functions.append(f)

        # 获取所有的 state variables
        self.state_var_written_functions_dict = dict()
        self.state_var_read_functions_dict = dict()
        self.state_var_read_in_require_functions_dict = dict()
        self.state_var_read_require_dict = dict()

        for svar in self.contract.state_variables:
            self.state_var_written_functions_dict[svar] = []
            self.state_var_read_functions_dict[svar] = []
            self.state_var_read_require_dict[svar] = []
            self.state_var_read_in_require_functions_dict[svar] = []

        for f in self.functions:
            for svar in f.function.all_state_variables_written():
                self.state_var_written_functions_dict[svar].append(f)
            for svar in f.function.all_state_variables_read():
                self.state_var_read_functions_dict[svar].append(f)

            for exp_req in f.requires:
                print(exp_req)
                for svar in exp_req.all_read_vars_group.state_vars:
                    self.state_var_read_require_dict[svar].append(exp_req)
                    self.state_var_read_in_require_functions_dict[svar].append(f)
            
            for key, value in self.state_var_read_in_require_functions_dict.items():
                self.state_var_read_in_require_functions_dict[key] = list(set(value))


    def get_function_from_signature(self, function_signature):
        """
            获取 public / external 函数
        """
        return next(
            (FunctionExp(f) for f in self.contract.functions if f.full_name == function_signature and not f.is_shadowed),
            None,
        )

    def get_written_functions(self,state_var) -> List[FunctionExp]:
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
        # 具体而言，我们检查 user_written_functions 中出现的 mapping owner candidates，如果和 owners 中匹配，我们认为它是 blackList / whiteList 而不是 owner
        bwList = []

        for ef in self.user_written_functions:
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
        for owner in self.owners:
            for f in self.state_var_read_in_require_functions_dict[owner]:
                f.owners.append(owner)

    def svar_only_updated_by_owner(self,state_var):
        """
            判断一个变量是否只能由 owner 更新（即除了构造函数外，存在一个由 owner 调用的赋值函数）
        """
        written_funcs = self.state_var_written_functions_dict[state_var]
        if len(written_funcs) == 0:
            return False

        for f in written_funcs:
            if len(f.owners) == 0:
                return False
        return True

    def _search_paused(self):
        """
            搜索所有的 paused
        """
        paused_candidates = []
        for f in self.user_written_functions:
            for exp_req in f.requires:
                if len(exp_req.all_read_vars_group.local_vars) > 0:
                    continue
                for svar in exp_req.all_read_vars_group.state_vars:
                    if svar.type == ElementaryType('bool'):
                        paused_candidates.append(svar)

        paused_candidates = list(set(paused_candidates))


        '''
        如果 user_written_functions 的 require 中存在一个 bool，且这个 bool only Owner 可以写，则存在暂停
        判断 bool 是否只和一个 constant 对比，（没有 local variables 出现在 require 中），判断 bool 相关的写函数是否 onlyowner
        '''

        paused = []
        for svar in paused_candidates:
            if self.svar_only_updated_by_owner(svar):
                paused.append(svar)

        self.paused = list(paused)

    def _search_totalSupply(self):
        f = self.get_function_from_signature('totalSupply()')

        if f is None:
            self.totalSupply = None
        else:
            f._get_returns()

            """
            # 识别 read state variables
            ts_candidates = [svar for svar in f.function.all_state_variables_read()
                if svar.type == ElementaryType('uint256')]

            if len(ts_candidates) == 1:
                self.totalSupply = ts_candidates[0]
            else: # 如果有多个 totalSupply
                print(ts_candidates)
            """

    def _search_identifies(self):
        """
            一个代币使用 name 和 symbol 的方式来标识自己，搜索所有的 name 和 symbol
            ERC20 是标准接口，ERC721 是可选，ERC1155 则不需要

            TODO: 这种判定是不完全的，因为：可能并没有 标准的读操作，但是存在写操作，这样就无法识别，
            因此需要加上对每个写函数的判定，如果这个写函数是 onlyowner，并且写入了一个 name 或 symbol，则认为是标识

        """
        
        identify_function_sigs = [
            'name()','symbol()','tokenURI()'
        ]
        identify_functions = []
        for id_fs in identify_function_sigs:
            f = self.get_function_from_signature(id_fs)
            if f is not None:
                identify_functions.append(f)
        
        identifies = []
        for f in identify_functions:
            identifies += [svar for svar in f.function.all_state_variables_read() if svar.type == ElementaryType('string')]

        self.identifies = list(set(identifies))


    def _search_user_state_vars(self):
        """
            搜索用户调用的标准接口中所有变量，如：手续费，balance，
            如果这些变量，owner 也可以修改，则这些变量是 unfair_settings

            用户可以写，owner 也可以写，用户不能写， owner 可以写
        """

        user_state_variables = []
        for f in self.user_written_functions:
            #if f.function.is_constructor: continue
            print('---',f,list2str( f.function.all_state_variables_read()))
            user_state_variables += f.function.all_state_variables_read()
        
        other_variables = self.paused + self.identifies + [self.totalSupply] + self.bwList + self.owners
        self.user_state_variables = list(set(user_state_variables)-set(other_variables))

    def _serach_lack_event_functions(self):
        """
            TODO:需要再次确认， owner 的函数是否需要 event
            如果一个 function 写了 state variable，则应当发送一个 event，提醒用户，这里寻找缺少的 event 的 function。
            我们并不考虑 event 的参数，关于 event 和实际操作不一致的问题：TokenScope: Automatically Detecting Inconsistent Behaviors of Cryptocurrency Tokens in Ethereum
        """
 
        for f in self.state_var_written_functions:
            if not f.function.is_constructor and len(f.events) == 0:
                self.lack_event_functions.append(f)


    def __str__(self) -> str:
        return self.contract.name

    def print(self):

        print('owner:',list2str(self.owners))
        for svar in self.owners:
            print(svar.name,list2str(self.state_var_written_functions_dict[svar]))
        print('bwList:',list2str(self.bwList))
        print('paused:',list2str(self.paused))
        
        print('totalSupply:',self.totalSupply)

        print('identifies:',list2str(self.identifies))
        print('user_state_variables:',list2str(self.user_state_variables))
        print('lack_event_functions:',list2str(self.lack_event_functions))




def list2str(l):
    l = [str(i) for i in l]
    return ','.join(l)
    