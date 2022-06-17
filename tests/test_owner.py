
from test_base import *
import logging
#logging.basicConfig(level=logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger()

def test_require_nodes():
    set_solc('0.8.1')
    slither = Slither("tests/contracts/owner_1.sol")
    cs =  slither.contracts_derived
    contract = cs[0]

    logger.info(contract.name)

    for fun in contract.functions_entry_points:
        logger.info(fun.name)
        fun = FunctionExp(fun)
        for n in fun.requireNodes:
            print(n)

def test_owners():

    set_solc('0.8.1')
    slither = Slither("tests/contracts/owner_1.sol")
    cs =  slither.contracts_derived
    contract = cs[0]
    contract = ContractExp(contract)
    print(contract.name)

   

    #owners = [] # owner candidates
    #for sv in contract.state_variables:
        #is_owner(sv)



def is_owner(svar):
    '''
        判断一个 static 是否为 owner
        1. owner 需要是 state variable
        2. owner 的类型是 address 或 mapping()
        3. owner 如果存在写函数，
            3.1 为构造函数
         或 3.2 写函数被 require 或 assert 约束，且约束条件中包含 state var, msg.sender
    '''

    logger.info("---is owner:{}".format(svar))
    if not isinstance(svar, StateVariable): return False
    if not svar.type == ElementaryType('address') and not (isinstance(svar.type, MappingType) and svar.type.type_from == ElementaryType('address')):
        return False
    func_writed_to_owner = []
    funcs = get_functions_writing_to_variable(svar)
    for fun in funcs:
        if fun.is_constructor:
            func_writed_to_owner.append(fun)
            continue 
        

        # 检查所有的写函数中，是否都被 require 或 assert 约束
        #for node in exp_all_require_or_assert_nodes(fun):
            #logger.info('\n\n')
            #logger.info('check require or asset {}'.format(node))
            #require_split(node)
          
            # 追踪 node 依赖的 variables
            #dep_vars, dep_irs_ssa = node_track(node)



def get_functions_writing_to_variable(var: "Variable"):
    return [f for f in var.contract.functions_entry_points if var in f.all_state_variables_written()]

def exp_all_require_or_assert_nodes(fun):
    nodes = [node for node in fun.all_nodes() if node.contains_require_or_assert()]
    return nodes

if __name__ == "__main__":
    test_require_nodes()
   # test_owners()