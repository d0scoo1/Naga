"""
    我们获取 IERC 作为判断是否实现了 ERC20/721/777/1155 接口的依据
"""

import subprocess
def set_solc(solc_ver):
    '''
    set the global solc version
    '''
    subprocess.run(["solc-select", "use", solc_ver], stdout=subprocess.PIPE, check=True)

from collections import namedtuple
ERC_FUNCTION = namedtuple("ERC_FUNCTION", ["full_name", "name", "parameters", "return_type","visibility", "view", "events"])
ERC_EVENT = namedtuple("ERC_EVENT", ["full_name","name", "parameters", "indexes"])

from slither.core.solidity_types.array_type  import ArrayType
from slither import Slither
from slither.slithir.operations.event_call import EventCall
def _get_contract_function_signatures(contract):
    ERC_SIGS = []
    for function in contract.functions_declared:
        
        events = []
        for op in function.all_slithir_operations():
            if isinstance(op,EventCall):
                events.append(op.name + "(" + ",".join([a.type.__str__() for a in op.read]) + ")" )

        return_type = []
        if function.return_type:
            return_type = [r.__str__() for r in function.return_type]
        ERC_SIGS.append(ERC_FUNCTION(function.full_name,function.name, [p.type.__str__() for p in function.parameters],return_type,function.visibility,function.view,events))
    
    return ERC_SIGS

def _get_contract_event_signatures(contract):
    ERC_SIGS = []
    for event in contract.events:
        ERC_SIGS.append(ERC_EVENT(event.full_name,event.name,[e.type.__str__() for e in event.elems],None))
    return ERC_SIGS

def _load_contract(path,contract_name=None):
    slither = Slither(path)
    return slither.get_contract_from_name(contract_name)[0]

import os
def _get_token_signatures(token_folder_path,erc):
    """
    获取ERC20/721/777/1155 等接口和实现的 FUNCTION 和 EVENT full name
    Args:
        token_folder_path: token 文件夹路径
        erc: ERC20/721/777/1155
    Returns:
        IERC_FUNCTIONS,
        IERC_EVENTS,
        ERC_FUNCTIONS,
        ERC_EVENTS,
    """
    interface_erc = _load_contract(os.path.join(token_folder_path,erc,"I"+erc+".sol"), "I"+erc)
    implemented_erc = _load_contract(os.path.join(token_folder_path,erc,erc+".sol"), erc)

    IERC_FUNCTIONS = _get_contract_function_signatures(interface_erc)
    IERC_EVENTS = _get_contract_event_signatures(interface_erc)
    ERC_FUNCTIONS = _get_contract_function_signatures(implemented_erc)
    ERC_EVENTS = _get_contract_event_signatures(implemented_erc)


    return  {
        "I"+erc+"_FUNCTIONS": IERC_FUNCTIONS,
        "I"+erc+"_EVENTS": IERC_EVENTS,
        erc+"_FUNCTIONS": ERC_FUNCTIONS,
        erc+"_EVENTS": ERC_EVENTS,
    }
    
def _write_erc_sigs(file_name,token_folder_path,erc):
    ERCs = _get_token_signatures(token_folder_path,erc)
    with open(file_name,"a+") as fw:
        fw.write('\n')
        for k,v in ERCs.items():
            fw.write(k + " = [\n")
            for fun in v:
                fw.write("    " + type(fun).__name__ + "(" + ",".join(["\""+str(v) + "\"" for v in fun]) + ")"  + ",\n")
            fw.write("]\n")
        
        for k,v in ERCs.items():
            fw.write(k + "_SIG = [\n")
            for fun in v:
                fw.write("\"" + fun.full_name + "\"" + ",")
            fw.write("]\n")
        fw.close()


"""
    每次解析 openzeppelin 会增加许多时间，因此我们将 token 中 functions 提前输出到 erc.py, 这样直接引用 erc.py 就行
"""
set_solc("0.8.1")
token_folder_path = "openzeppelin-contracts/0.8/contracts/token/"

with open("token.py", "w+") as fw:
    fw.write("from collections import namedtuple\n"+
        "ERC_FUNCTION = namedtuple(\"ERC_FUNCTION\", [\"full_name\", \"name\", \"parameters\", \"return_type\",\"visibility\", \"view\", \"events\"])\n"+
        "ERC_EVENT = namedtuple(\"ERC_EVENT\", [\"full_name\",\"name\", \"parameters\", \"indexes\"])\n")
    fw.close()

for erc in ["ERC20","ERC721","ERC777","ERC1155"]:
    _write_erc_sigs('token.py',token_folder_path,erc)
