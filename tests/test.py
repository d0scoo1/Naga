
from test_base import *


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

def test_compile(path):

    write_log("\n####" + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + "####\n")
    contracts = load_contractsJson(path)

    contracts_path = os.path.join(path,'contracts')
    for version in tqdm(os.listdir(contracts_path)):
        if version == 'noSolc':
            continue

        if version.startswith('0.4.'):
            continue
        set_solc(version)

        #solc_remaps = get_solc_remaps(version)
        version_path = os.path.join(contracts_path, version)

        for addr in os.listdir(version_path):
            addr_path = os.path.join(version_path, addr)

            sol_path = find_contract_file(addr_path,contracts[addr]['ContractName'])

            naga = Naga(Slither(sol_path),contracts[addr]['ContractName'])
            if len(naga.main_contracts) != 1:
                print('#',len(naga.main_contracts),sol_path)

            #print(sol_path)
            #write_log('\n'+sol_path)
            
                #write_log(c.summary())

            '''
            try:
                #slither = Slither(sol_path, solc_remaps=solc_remaps)
                slither = Slither(sol_path)
                for c in slither.contracts_derived:
                    c = ContractExp(c)
                    write_log(c.contratc.name+'\n')
                    print(c.summary())
            except:
                write_error('\"'+sol_path+'\",\n')
            '''

log_path = 'logs.txt'
def write_log(content):
    with open(log_path,"a") as fw:
        fw.write(content)
    fw.close()

def write_error(content):
    with open('errors.txt',"a") as fw:
        fw.write(content)
    fw.close()

def find_contract_file(addr_path,contractName):
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


from naga.naga import Naga
def test_compile2(path="/mnt/c/users/vk/naga/tokens/token20"):
    contracts = load_contractsJson(path)

    sol_path = '/mnt/c/users/vk/naga/tokens/token20/contracts/0.6.10/0x0b498ff89709d3838a063f1dfa463091f9801c2b/SetToken.sol'
    ss = sol_path.split("/")
    address = ss[-2]
    version = ss[-3]
    set_solc(version)
    addr_path = ''
    for i in ss[0:-1]:
        addr_path = addr_path + i + '/'

    sol_path = find_contract_file(addr_path,contracts[address]['ContractName'])
 
    print(sol_path)
    slither = Slither(sol_path)
    naga = Naga(slither)
    naga.summary()
    for c in naga.contracts_erc20:
        print(c.summary())
        for sve in c.all_exp_state_vars:
            print(sve.summary())

from naga.core.detectors import(LackEvents,Paused)
def test_20():
    set_solc('0.6.10')
    slither = Slither('/mnt/c/users/vk/naga/tokens/token20/contracts/0.6.10/0x0b498ff89709d3838a063f1dfa463091f9801c2b/SetToken.sol')
    naga = Naga(slither,'SetToken')
    for c in naga.main_contracts:
        print(c)
        c.detect_erc20()
        print(c.summary())
        #c.register_detector(LackEvents)
        #c.register_detector(Paused)



if __name__ == "__main__":
    #test_compile('/mnt/c/users/vk/naga/tokens/token20')
    #test_compile2()
    test_20()