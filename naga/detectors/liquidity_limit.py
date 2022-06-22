from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.mapping_type import MappingType

def liquidity_limit(exp_contract):
    """
        判断 transfer(address,uint),transferFrom(address,address,uint256) 中是否有 暂停，黑名单
    """

    func_sigs = ["transfer(address,uint256)", "transferFrom(address,address,uint256)"]

    exp_functions = []
    for fs in func_sigs:
        f = exp_contract.get_function_from_signature(fs)
        if f is not None:
            exp_functions.append(f)

    # 检索所有 function 中的 require

    paused_candidates = []
    bwList_candidates = [] # black list/white list
    for exp_func in exp_functions:
        for exp_req in exp_func.all_exp_requires:
            if len(exp_req.read_var_group.local_vars) > 0 or len(exp_req.read_var_group.state_vars) == 0:
                continue
            for svar in exp_req.read_var_group.state_vars:
                if svar.type == ElementaryType('bool'):
                    paused_candidates.append((svar,exp_func,exp_req))
                elif isinstance(svar.type, MappingType) and svar.type.type_from == ElementaryType('address') and svar.type.type_to == ElementaryType('bool'):
                    bwList_candidates.append((svar,exp_func,exp_req))

    
    

    '''
        如果存在一个 mapping(address => bool)，且这个 mapping only Owner 可以写，则存在黑名单
    '''


