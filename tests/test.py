
from test_base import *


def test():
    set_solc('0.4.17')
    slither = Slither("tests/contracts/token_20_0xdAC17F958D2ee523a2206206994597C13D831ec7.sol")
    for c in slither.contracts_derived:
        print('contract:', c.name)
        for f in c.functions_entry_points:
            print('function:', f.name)
           
        #print(balance(ContractExp(c)))
        #liquidity_limit(ContractExp(c))
        print('\n')


def balance(contract):
    """
        balance 表示账户的余额，它影响着流动性
            type: mapping(address => uint)
            writed functions: transfer(address,uint),transferFrom(address,address,uint256)
            read functions: balanceOf(address)
    """

    func_sigs = ["balanceOf(address)", "transfer(address,uint256)", "transferFrom(address,address,uint256)"]

    for fs in func_sigs:
        for f in contract.get_declared_function_from_signature(fs):
            for svar in f.all_state_variables_read():
                if isinstance(svar.type, MappingType) and svar.type.type_from == ElementaryType('address') and svar.type.type_to.__str__().startswith('uint'):
        #svar.type.type_to == ElementaryType('uint'):
                    return svar
    return None

def liquidity_limit(contractExp):
    """
        判断 transfer(address,uint),transferFrom(address,address,uint256) 中是否有 暂停，黑名单
    """
    contract = ContractExp(contract)
    func_sigs = ["transfer(address,uint256)", "transferFrom(address,address,uint256)"]

    functions_exp = []
    for fs in func_sigs:
        functions_exp += contract.get_declared_function_from_signature(fs)

    # 检索所有 function 中的 require

    bool_vars = []
    mapping_vars = []
    for fe in functions_exp:
        print(fe.function.name)
        for req in fe.requireNodes:
            if len(req.cond_read_vars.local_vars) > 0 or len(req.cond_read_vars.state_vars) == 0:
                continue
            for svar in req.cond_read_vars.state_vars:
                if svar.type == ElementaryType('bool'):
                    bool_vars.append((svar,fe))
                    print((svar,fe))
                elif isinstance(svar.type, MappingType) and svar.type.type_from == ElementaryType('address') and svar.type.type_to == ElementaryType('bool'):
                    mapping_vars.append((svar,fe))
    """
    bool_vars = []
    mapping_vars = []
    for f in functions:
        for svar in all_state_variables_in_require(f): # 判断 
            if svar.type == ElementaryType('bool'):
                bool_vars.append((svar,f))
            elif isinstance(svar.type, MappingType) and svar.type.type_from == ElementaryType('address') and svar.type.type_to == ElementaryType('bool'):
                mapping_vars.append((svar,f))
    
    for v in bool_vars + mapping_vars:
        print(v[0],v[1])
    """

    '''
        如果 require 中存在一个 bool，且这个 bool only Owner 可以写，则存在暂停
        判断 bool 是否只和一个 constant 对比，（没有 local variables 出现在 require 中），判断 bool 相关的写函数是否 onlyowner
    '''


    '''
        如果存在一个 mapping(address => bool)，且这个 mapping only Owner 可以写，则存在黑名单
    '''


def all_require_variables(func):
    """
        返回 require 依赖的变量 
    """
    return func.all_state_variables_read()

def all_variables_in_require(func):
    """
        返回 func 中所有 require 中所有的变量
    """
    return func.all_state_variables_read()

def all_state_variables_in_require(func):
    return func.all_state_variables_read()

def all_local_variables_in_require(func):
    pass

def isWriteable(state_var):
    """
        判断一个变量是否可写。 paused 变量，需要可以写，并且只能 owner 写（以切换状态）。而 owner 变量由 constructor 赋值，因此可以不存在 写 操作，如果存在写操作，也只能由 owner 写
    """
    pass


def isOnlyOwner(state_var):
    """
        判断一个变量是否只有Owner可以写
    """
    pass


'''
    function 层面：
        读写的变量，可由 all_state_variables_read 获得
        require 中读写的变量，我们使用 depVars 对象
        是否 onlyOwner 
    contract 层面：
        给出一个变量，可以查到所有 function, require 读写

'''

if __name__ == "__main__":
    test()
