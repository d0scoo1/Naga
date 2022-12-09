from typing import List, Dict,Optional
from slither.core.declarations import Contract
from slither.core.variables.state_variable import StateVariable
import json

from .function_naga import FunctionN
from .state_variable_naga import VarLabel, DType, DMethod, StateVarN
from naga.detectors import AccessControl


ERC20_WRITE_FUNCS_SIG = [
    "transfer(address,uint256)",
    "approve(address,uint256)",
    "transferFrom(address,address,uint256)",
]

ERC721_WRITE_FUNCS_SIG = [
    "safeTransferFrom(address,address,uint256)",
    "transferFrom(address,address,uint256)",
    "approve(address,uint256)",
    "setApprovalForAll(address,bool)",
    "safeTransferFrom(address,address,uint256,bytes)"
]

ERC1155_WRITE_FUNCS_SIG = [
    "setApprovalForAll(address,bool)",
    "safeTransferFrom(address,address,uint256,uint256,bytes)",
    "safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)"
]

class ContractN():
    def __init__(self, contract:Contract, naga = None):
        self.naga = naga
        self.contract = contract # Slither Contract
        self.name = contract.name # Contract name
        
        self._is_erc20:Optional[bool] = None
        self._is_erc721:Optional[bool] = None
        self._is_erc1155:Optional[bool] = None
        self.erc_force = None
        self.is_analyzed = False

        self.detectors = []

        self.summary = dict()

    @property
    def is_erc20(self) -> bool:
        if self._is_erc20 is None:
            funcs_sig = [f.full_name for f in self.contract.functions_entry_points]
            if len(set(ERC20_WRITE_FUNCS_SIG) - set(funcs_sig)) == 0:
                self._is_erc20 = True
            else:
                self._is_erc20 = False
        return self._is_erc20
    
    @property
    def is_erc721(self) -> bool:
        if self._is_erc721 is None:
            funcs_sig = [f.full_name for f in self.contract.functions_entry_points]
            if len(set(ERC721_WRITE_FUNCS_SIG) - set(funcs_sig)) == 0:
                self._is_erc721 = True
            else:
                self._is_erc721 = False
        return self._is_erc721

    @property
    def is_erc1155(self) -> bool:
        if self._is_erc1155 is None:
            funcs_sig = [f.full_name for f in self.contract.functions_entry_points]
            if len(set(ERC1155_WRITE_FUNCS_SIG) - set(funcs_sig)) == 0:
                self._is_erc1155 = True
            else:
                self._is_erc1155 = False
        return self._is_erc1155
    
    @property
    def erc(self):
        if self.erc_force is not None: return self.erc_force
        if self.is_erc20: return 'erc20'
        if self.is_erc721: return 'erc721'
        if self.is_erc1155: return 'erc1155'
        return None
    
    @property
    def is_erc(self):
        return self.is_erc20 or self.is_erc721 or self.is_erc1155 or (self.erc_force != None)

    @property
    def is_upgradeable(self) -> bool:
        return self.contract.is_upgradeable
    
    @property
    def is_upgradeable_proxy(self) -> bool:
        return self.contract.is_upgradeable_proxy

    def analyze(self):
        # 
        self._dividing_variables_functions()
        # 初始化变量分析池
        self.svarn_pool = dict()
        for sv in self.all_state_vars:
            self.svarn_pool[sv] = StateVarN(sv)

        # 查找 AC 变量
        ac = AccessControl(self.naga,self)
        ac.detect()
        self.detectors.append(ac)

        # 查找完AC变量后，更新变量 rw
        for svar,svarn in self.svarn_pool.items():
            if svarn.external: continue
            svarn.rw = get_svar_rw(self,svar)

        for svar,svarn in self.svarn_pool.items():
            if not svarn.external: continue
            self.update_external_svarn_rw(svarn)
       
        self.is_analyzed = True
        
        if self.naga != None:
            self.naga.contracts_analyzed.append(self)

    def _dividing_variables_functions(self):
        self.functions: List["FunctionN"] = [] # All entry functions
        self.state_var_written_functions: List["FunctionN"] = []
        self.state_var_read_functions: List["FunctionN"] = []
        self.state_var_written_functions_dict:Dict("StateVariable",["FunctionN"]) = dict()
        self.state_var_read_functions_dict:Dict("StateVariable",["FunctionN"]) = dict()
        self.state_var_read_in_condition_functions_dict: Dict("StateVariable",["FunctionN"]) = dict()
        self.state_var_read_in_conditions_dict: Dict("StateVariable",["ConditionNode"]) = dict()
        self.all_state_vars: List["StateVariable"] = []

        # Functions defined in the token contract
        self.token_write_function_sigs = list(set(ERC20_WRITE_FUNCS_SIG+ERC721_WRITE_FUNCS_SIG+ERC1155_WRITE_FUNCS_SIG))
        self.token_written_functions: List["FunctionN"] = [] # 接口中定义的用户的写函数，我们通过这些函数来判定一个 owner 是否为 bwList 或 paused

        for f in self.contract.functions_entry_points: # functions_declared():
            f = FunctionN(f,self)
            self.functions.append(f)
            if len(f.function.all_state_variables_read()) > 0:
                self.state_var_read_functions.append(f)
            if len(f.function.all_state_variables_written()) > 0:
                self.state_var_written_functions.append(f)
        
        # Get all transfer functions
        for f in self.functions:
            if f.function.full_name in self.token_write_function_sigs:
                self.token_written_functions.append(f)
        
        all_state_vars = self.contract.all_state_variables_written + self.contract.all_state_variables_read

        for f in self.functions:
            for svar in f.function.all_state_variables_written() + f.function.all_state_variables_read():
                all_state_vars.append(svar)
            for cond in f.conditions:
                for svar in cond.dep_vars_groups.state_vars:
                    all_state_vars.append(svar)

        self.all_state_vars = list(set(all_state_vars))

        for s in self.all_state_vars:
            self.state_var_written_functions_dict[s] = []
            self.state_var_read_functions_dict[s] = []
            self.state_var_read_in_conditions_dict[s] = []
            self.state_var_read_in_condition_functions_dict[s] = []

        for f in self.functions:
            for svar in f.function.all_state_variables_written():
                self.state_var_written_functions_dict[svar].append(f)
            for svar in f.function.all_state_variables_read():
                self.state_var_read_functions_dict[svar].append(f)

            for cond in f.conditions:
                #print(cond)
                for svar in cond.dep_vars_groups.state_vars:
                    self.state_var_read_in_conditions_dict[svar].append(cond)
                    self.state_var_read_in_condition_functions_dict[svar].append(f)
            
            for svar, value in self.state_var_read_in_condition_functions_dict.items():
                self.state_var_read_in_condition_functions_dict[svar] = list(set(value))

    # svars_pool
    def update_svarn_label(self, svar, v_lable: VarLabel, d_type:DType,d_method:DMethod,caller_dict = {}):
        if svar not in self.svarn_pool:
            callers = []
            if svar in caller_dict: callers = caller_dict[svar]
            ex_svarn = StateVarN(svar,external = True, callers = callers)
            self.svarn_pool[svar] = ex_svarn
            self.update_external_svarn_rw(ex_svarn) # 直接更新变量 rw

        self.svarn_pool[svar].label = v_lable
        self.svarn_pool[svar].dType = d_type
        if d_method is not None:
            self.svarn_pool[svar].dMethods[d_method] = True

    def get_svars_by_label(self, v_lable: VarLabel = None):
        return [svar for svar in self.svarn_pool if self.svarn_pool[svar].label == v_lable and not self.svarn_pool[svar].external]

    def get_svars_by_dtype(self, d_type:DType = None):
        return [svar for svar in self.svarn_pool if self.svarn_pool[svar].dType == d_type and not self.svarn_pool[svar].external]

    def get_all_svars_by_label(self, v_lable: VarLabel = None):
        return [svar for svar in self.svarn_pool if self.svarn_pool[svar].label == v_lable]

    def get_all_svars_by_dtype(self, d_type:DType = None):
        return [svar for svar in self.svarn_pool if self.svarn_pool[svar].dType == d_type]

    def update_external_svarn_rw(self,svarn):
        """
        external variable 由 2 个地方决定：
            external contract 中的 rw 和 dom_caller 的 rw
        """
        for dom in svarn.callers:
            ec_name = dom.dest_contract
            external_contract = [c for c in self.naga.contracts_analyzed if c.name == ec_name]
            if len(external_contract) == 0:
                external_contract = self.naga.slither.get_contract_from_name(ec_name)
                if len(external_contract) == 1:
                    external_contract = ContractN(external_contract[0],self.naga)
                    external_contract.analyze()
                else:
                    return
            else:
                external_contract = external_contract[0]
            if svarn.svar in external_contract.svarn_pool:
                svarn.rw = external_contract.svarn_pool[svarn.svar].rw
        
        for dom in svarn.callers:
            for dom_svar in dom.state_var_callers():
                if self.svarn_pool[dom_svar].rw[3] == 1:
                    svarn.rw[3] = 1
    
    def svar_written_functions(self,svar):
        '''
        state_var_written_functions_dict 中包括了 初始化函数，这里需要去掉
        '''
        return [
            f 
            for f in self.state_var_written_functions_dict[svar]
            if not f.is_constructor_or_initializer
        ]


    from naga.utils import collect_summary
    def output(self,output_file=None):
        self.collect_summary()
        self.summary_json = json.dumps(self.summary,indent=2)

        if output_file is None:
            return self.summary_json
        with open(output_file,'w') as f:
            f.write(self.summary_json)
        return self.summary_json


def get_svar_read_written_functions(self, state_var):
        """
        Users and owners read and write permissions on state variables
        """
        functions_user_read: List["FunctionN"] = []
        functions_user_written: List["FunctionN"] = []
        functions_owner_read: List["FunctionN"] = []
        functions_owner_written: List["FunctionN"] = []

        for rf in self.state_var_read_functions_dict[state_var]:
            if rf.is_constructor_or_initializer: continue
            if rf in self.owner_in_condition_functions:
                functions_owner_read.append(rf)
            else:
                functions_user_read.append(rf)

        for wf in self.state_var_written_functions_dict[state_var]:
            if wf.is_constructor_or_initializer: continue
            if wf in self.owner_in_condition_functions:
                functions_owner_written.append(wf)
            else:
                functions_user_written.append(wf)
        
        return functions_user_read, functions_user_written, functions_owner_read, functions_owner_written

def get_svar_rw(self,svar):
        fs_u_r,fs_u_w,fs_o_r,fs_o_w = get_svar_read_written_functions(self,svar)
        rw = [0,0,0,0]
        if len(fs_u_r) > 0: rw[0] = 1
        if len(fs_u_w) > 0: rw[1] = 1
        if len(fs_o_r) > 0: rw[2] = 1
        if len(fs_o_w) > 0: rw[3] = 1
        return rw
