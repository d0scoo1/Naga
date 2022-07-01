
from test_base import *
from naga.naga import Naga

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


def test_20():
    set_solc('0.5.12')
    sol_file = '/mnt/c/users/vk/naga/tokens/token20/contracts/0.5.12/0x5d3a536e4d6dbd6114cc1ead35777bab948e3643/CErc20Delegator.sol'
    print(sol_file)
    slither = Slither(sol_file)
    naga = Naga(slither,'CErc20Delegator','0x33db8d52d65f75e4cdda1b02463760c9561a2aa1')

    for c in naga.main_contracts:
        if c.is_erc20:
            c.detect_erc20()
            for svar in c.label_svars_dict['owners']:
                print(svar)

            print(c.summary_json())
            #line_dict,title,line = c.summary_csv()
            #print(title)

def test():
    set_solc('0.5.12')
    sol_file = '/mnt/c/users/vk/naga/tokens/token20/contracts/0.5.12/0x5d3a536e4d6dbd6114cc1ead35777bab948e3643/CErc20Delegator.sol'
    print(sol_file)
    slither = Slither(sol_file)
    naga = Naga(slither,'CErc20Delegator','0x312ca0592a39a5fa5c87bb4f1da7b77544a91b87','erc20','0.5.12')

    for c in naga.entry_contracts:
        c.detect()
        for svar in c.label_svars_dict['owners']:
            print(svar)

        print(c.summary_json())

if __name__ == "__main__":
    #test_compile2()
    #test_20()
    test()