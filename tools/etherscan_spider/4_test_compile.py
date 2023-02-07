from solc_utils import set_solc,get_solc_versions,get_solc_remaps
from slither import Slither
from tqdm import tqdm
import os
import json
from token_info import token_list as token
import time

def test_compile(path):

    write_log(os.path.join(path, "logs"),"\n####" + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + "####\n")
    contracts = load_contractsJson(path)

    contracts_path = os.path.join(path,'contracts')
    for version in tqdm(os.listdir(contracts_path)):
        if version == 'noSolc':
            continue
        set_solc(version)

        #solc_remaps = get_solc_remaps(version)
        version_path = os.path.join(contracts_path, version)

        for addr in os.listdir(version_path):
            addr_path = os.path.join(version_path, addr)

            sol_path = find_contract_name(addr_path,contracts[addr]['ContractName'])

            try:
                #slither = Slither(sol_path, solc_remaps=solc_remaps)
                slither = Slither(sol_path)
            except:
                write_log(os.path.join(path,"logs"),'\"'+sol_path+'\",\n')

def write_log(log_path,content):
    with open(log_path,"a") as fw:
        fw.write(content)
    fw.close()

def load_contractsJson(path):
    contracts = {}
    with open(os.path.join(path, 'contracts.json'), 'r') as fr:
        line = fr.readline()
        while line != '':
            c = json.loads(line)
            contracts[c['address']] = c
            line = fr.readline()
        fr.close()
    return contracts


def find_contract_name(addr_path,contractName):
    sol_path = os.path.join(addr_path,contractName+".sol")
    if os.path.exists(sol_path):
        return sol_path

    normal_sol = {'Context','IERC20','Ownable','SafeMath','ECDSA','Address','Counters','AccessControl','ERC721Enumerable','IERC721Metadata','IERC165','IERC721','IERC721','ReentrancyGuard'}

    sol_set = set()
    for s in os.listdir(addr_path):
        sol_set.add(s[:-4]) #去掉.sol

    candidate = sol_set - normal_sol
    if len(candidate) == 0:
        candidate = sol_set

    index = 1
    #寻找首先匹配
    while len(candidate) > 1 or index < len(contractName):
        del_list = set()
        for s in candidate:
            if contractName[0:index].lower() != s[0:index].lower():
                del_list.add(s)
        candidate = candidate - del_list
        index = index + 1

    if len(candidate) == 1:
        return os.path.join(addr_path,candidate.pop()+".sol")

    ''' # 寻找最大匹配的
    for i in range(1,len(contractName)-1):  #,最少有2个匹配
        cn = contractName[0:len(contractName)-i]
        for s in sol_set:
            if cn in s:
                return s
    '''
    return os.path.join(addr_path,sol_set.pop()+".sol")



def test_compile2(path):

    contracts = load_contractsJson(path)
    error_contracts = [
    ]

    for sol in tqdm(error_contracts):
        ss = sol.split("/")
        address = ss[-2]
        version = ss[-3]
        set_solc(version)
        addr_path = ''
        for i in ss[0:-1]:
            addr_path = addr_path + i + '/'

        sol_path =  find_contract_name(addr_path,contracts[address]['ContractName'])
        try:
            slither = Slither(sol_path) #, solc_remaps=get_solc_remaps(version)
        except:
            write_log(os.path.join(path,"logs"),'\"'+sol_path+'\",\n')
            #print(sol_path)

def test(path):
    contracts = load_contractsJson(path)
    raw_path = ""
    sol_path = "/mnt/c/users/vk/naga/tokens/token721/contracts/0.8.9/0xb543f9043b387ce5b3d1f0d916e42d8ea2eba2e0/fiveoutofnine.sol"
    ss = sol_path.split("/")
    address = ss[-2]
    version = ss[-3]
    set_solc(version)
    addr_path = ''
    for i in ss[0:-1]:
        addr_path = addr_path + i + '/'

    sol_path = find_contract_name(addr_path,contracts[address]['ContractName'])

    slither = Slither(sol_path, solc_remaps = get_solc_remaps(version))


if __name__=='__main__':
    #test_compile(token['20'].path)
    #test_compile2(token['721'].path)
    #test_compile2(token['1155'].path)
    print()

    #test(token['721'].path)
