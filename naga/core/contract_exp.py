from typing import List, Dict,Optional
from slither.core.declarations import Contract
from slither.core.variables.state_variable import StateVariable
from .function_exp import FunctionExp
from .condition_exp import ConditionNode
#from naga.core.openzeppelin import (ERC20_WRITE_FUNCS_SIG,ERC721_WRITE_FUNCS_SIG,ERC1155_WRITE_FUNCS_SIG)
import json

ERC20_WRITE_FUNCS_SIG = ["transfer(address,uint256)","approve(address,uint256)","transferFrom(address,address,uint256)"]
ERC721_WRITE_FUNCS_SIG = ["safeTransferFrom(address,address,uint256)","transferFrom(address,address,uint256)","approve(address,uint256)","setApprovalForAll(address,bool)","safeTransferFrom(address,address,uint256,bytes)"]
ERC1155_WRITE_FUNCS_SIG = ["setApprovalForAll(address,bool)","safeTransferFrom(address,address,uint256,uint256,bytes)","safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)"]

from naga.detectors import (
        AccessControl,Pause,ERCMetadata,TradingParams,MissingEvent,)
from naga.detectors.abstract_detector import(StateVarExp)
class ContractExp():
    def __init__(self,contract:Contract,nagaObj) -> None:
        self.contract = contract
        self.naga = nagaObj
        self._is_erc20: Optional[bool] = None
        self._is_erc721: Optional[bool] = None
        self._is_erc1155: Optional[bool] = None
        self.info = dict()
        self.is_analyzed = False
        self._summary = None

    def set_info(self, info):
        '''
        Those extra info will be recorded at the head of summary.
        '''
        self.info = info
    
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
    def get_erc_str(self):
        if self.is_erc20: return 'erc20'
        if self.is_erc721: return 'erc721'
        if self.is_erc1155: return 'erc1155'
        return None
    
    @property
    def is_erc(self):
        return self.is_erc20 or self.is_erc721 or self.is_erc1155
    
    @property
    def is_upgradeable(self) -> bool:
        return self.contract.is_upgradeable
    
    @property
    def is_upgradeable_proxy(self) -> bool:
        return self.contract.is_upgradeable_proxy

    def __str__(self) -> str:
        return self.contract.name

    #######################################
    ####        Detect  Functions      ####
    #######################################

    def analysis(self):
        self._dividing_functions()
        self.exp_svars_dict = dict() # svar:StateVariable -> (label:str, rw:str)
        for svar in self.all_state_vars:
            self.exp_svars_dict[svar] = StateVarExp(svar)
        ac = AccessControl(self) # 必须是第一个，它包含初始化和其他 detectors 依赖的信息
        ac.detect()
        self.is_analyzed = True

    def detect(self,erc_force = None):
        self.erc_force = erc_force
        erc = self.get_erc_str
        if erc_force is not None: erc = erc_force
        
        '''
        在其他的 detector 执行前，我们需要
        1. 划分需要的 function 分类
        2. 检测 owner 权限 (AccessControl, 顺便检测了出了 bwList 和部分 paused)
        3. 根据检测结果，划分变量为 user, owner 的读写权限
        '''
        if  not self.is_analyzed:
            self.analysis()
        
        self.detectors =[
            Pause(self),
            ERCMetadata(self,erc),
            TradingParams(self),
            MissingEvent(self),
        ]
        for detector in self.detectors:
            detector.detect()


    def _dividing_functions(self):
        self.functions: List["FunctionExp"] = [] # All entry functions
        self.state_var_written_functions: List["FunctionExp"] = []
        self.state_var_read_functions: List["FunctionExp"] = []
        self.state_var_written_functions_dict:Dict("StateVariable",["FunctionExp"]) = dict()
        self.state_var_read_functions_dict:Dict("StateVariable",["FunctionExp"]) = dict()
        self.state_var_read_in_condition_functions_dict: Dict("StateVariable",["FunctionExp"]) = dict()
        self.state_var_read_in_conditions_dict: Dict("StateVariable",["ConditionNode"]) = dict()
        self.all_state_vars: List["StateVariable"] = []

        # Functions defined in the token contract
        self.token_write_function_sigs = list(set(ERC20_WRITE_FUNCS_SIG+ERC721_WRITE_FUNCS_SIG+ERC1155_WRITE_FUNCS_SIG))
        self.token_written_functions: List["FunctionExp"] = [] # 接口中定义的用户的写函数，我们通过这些函数来判定一个 owner 是否为 bwList 或 paused

        for f in self.contract.functions_entry_points: # functions_declared():
            f = FunctionExp(f)
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

    def get_svar_read_written_functions(self, state_var):
        """
        Users and owners read and write permissions on state variables
        """
        functions_user_read: List["FunctionExp"] = []
        functions_user_written: List["FunctionExp"] = []
        functions_owner_read: List["FunctionExp"] = []
        functions_owner_written: List["FunctionExp"] = []

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

    def get_rw_str(self,svar):
        fs_u_r,fs_u_w,fs_o_r,fs_o_w = self.get_svar_read_written_functions(svar)
        rw_str = ""
        if len(fs_u_r) > 0: rw_str += '1'
        else: rw_str += '0'
        if len(fs_u_w) > 0: rw_str += '1'
        else: rw_str += '0'
        if len(fs_o_r) > 0: rw_str += '1'
        else: rw_str += '0'
        if len(fs_o_w) > 0: rw_str += '1'
        else: rw_str += '0'
        return rw_str

    from naga.printers import contract_summary
    @property
    def summary(self):
        if self._summary is None:
            self._summary = self.contract_summary()
        return self._summary
    def summary_json(self,output_file=None):
        summary_json = json.dumps(self.summary,indent=2)
        if output_file is not None:
            with open(output_file,'w') as f:
                f.write(summary_json)
            f.close()
        return summary_json

    '''
    def summary_csv(self):
        return self.contract_summary2csv()
    '''
    