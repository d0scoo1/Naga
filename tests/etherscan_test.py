import sys
sys.path.append(".")
print(sys.path)

from naga_test import NagaTest
import os
import json
from solc_utils import set_solc
from slither import Slither
from tqdm import tqdm
from naga.naga import Naga
import time

class EtherscanTest(NagaTest):
    def __init__(self, tag, contractsJson_path, contract_dir, output_dir, is_clean_env=False, erc_force=None) -> None:
        super().__init__(tag, contractsJson_path, contract_dir, output_dir, is_clean_env, erc_force)

    def _get_entry_contract(self,contract_addr_dir,contract_addr,contract_name):
        # slither checks whether a contract_name in the contract.
        sol_path = _get_entry_sol(contract_addr_dir,contract_name)
        try:
            cs = Slither(sol_path).get_contract_from_name(contract_name=contract_name)
            if len(cs) == 1:
                return sol_path
            # 如果没有，则尝试遍历文件查找
            for sol in os.listdir(contract_addr_dir):
                sol_path = os.path.join(contract_addr_dir,sol)
                cs = Slither(sol_path).get_contract_from_name(contract_name=contract_name)
                if len(cs) == 1:
                    return sol_path
                # 如果没有找到 entry contract
            self.not_find_entry_contract += 1
            self._write_line(self.error_logs,'slither,no contract,'+contract_addr+','+contract_name)
            return None
        except:
            self.slither_compiler_error += 1
            self._write_line(self.error_logs,'slither,compiler error,'+contract_addr+','+contract_name)
        return None
    
    def run(self):
        contractsJson = self.load_contractsJson()
        csv_first_line_is_written = False
        for version in tqdm(os.listdir(self.contract_dir)):
            if version == 'noSolc':
                continue
            # Skip the version that is 0.4.x
            if version.startswith('0.4.'): 
                self.contract_version_0_4 += 1
                continue
            # Set the solc version
            set_solc(version)
            version_dir = os.path.join(self.contract_dir, version)
            for contract_addr in os.listdir(version_dir):
                # Skip Proxy contracts
                if contractsJson[contract_addr]['Proxy'] == '1':
                    self.contract_is_proxy += 1
                    imp_contract_addr = contractsJson[contract_addr]['Implementation']
                    if imp_contract_addr in contractsJson:
                        self.proxy_has_implement += 1
                    continue
                # Skip contracts that have been tested
                if contract_addr in self.contracts_tested: continue

                addr_dir = os.path.join(version_dir, contract_addr)
                contract_name = contractsJson[contract_addr]['ContractName']
                sol_path = self._get_entry_contract(addr_dir,contract_addr,contract_name)
                if sol_path is None: continue
                try:
                    before_slither_compile = time.time()
                    slither = Slither(sol_path)
                    after_slither_compile = time.time()
                    slither_compile_cost = after_slither_compile - before_slither_compile
                    self.slither_compiler_cost += slither_compile_cost
                    self.slither_pass += 1
                    
                    before_naga_analyze = time.time()
                    naga = Naga(slither,contract_addr,contract_name,self.erc_force,version)
                    for contract in naga.entry_contracts:
                        contract.detect()
                        after_naga_analyze = time.time()
                        naga_analyze_cost = after_naga_analyze - before_naga_analyze
                        self.naga_test_cost += naga_analyze_cost

                        self.naga_test_success += 1

                        c_json_file = os.path.join(self.output_json_dir,contract_addr)
                        self._write_json(c_json_file, contract.summary_json())
                        
                        line_dict,first_line,line = contract.summary_csv()
                        if not csv_first_line_is_written:
                            self._write_line(self.output_csv,first_line)
                            csv_first_line_is_written = True
                        self._write_line(self.output_csv,line)

                        self._write_line(self.output_logs,contract_addr+","+contract_name+","+str(slither_compile_cost)+","+str(naga_analyze_cost))
                except:
                    self.naga_test_fail += 1
                    self._write_line(self.error_logs,'naga,detector error,'+contract_addr)
        
        super().output_test_summary()
    
    def get_proxy_contracts(self):
        """
            统计代理合约的数量，这不包括 upgradeable 合约
        """
        contractsJson = self.load_contractsJson()
        proxy_address_list = []
        for contract_addr in contractsJson:
            if contractsJson[contract_addr]['version'].startswith('0.4.'):
                continue
            if contractsJson[contract_addr]['Proxy'] == '1':
                proxy_address_list.append(contract_addr)
        return proxy_address_list

def _get_entry_sol(contract_addr_dir,contract_name):
    """
        有可能有多个文件，因此，我们需要找到入口文件，
        如果只有一个文件，则直接为入口文件
        如果有多个文件，检查是否有 contrac_name 相同的文件，如果有，则返回
    """
    sols = os.listdir(contract_addr_dir)
    if len(sols) == 1:
        return os.path.join(contract_addr_dir,sols[0])

    sol_path = os.path.join(contract_addr_dir,contract_name+".sol")
    if os.path.exists(sol_path):
        return sol_path
    
    ## 如果都没有，则首先删掉一些常见的文件，然后匹配最相似的名字
    normal_sol = {'Context','IERC20','Ownable','SafeMath','ECDSA','Address','Counters','AccessControl','ERC721Enumerable','IERC721Metadata','IERC165','IERC721','IERC721','ReentrancyGuard'}
    sol_set = set()
    for s in sols:
        sol_set.add(s[:-4]) #去掉.sol
    
    sol_candidates = sol_set - normal_sol
    if len(sol_candidates) == 0: sol_candidates = sol_set
    
    index = 1
    #寻找首先匹配
    while len(sol_candidates) > 1 or index < len(contract_name):
        del_list = set()
        for s in sol_candidates:
            if contract_name[0:index].lower() != s[0:index].lower():
                del_list.add(s)
        sol_candidates = sol_candidates - del_list
        index = index + 1
    if len(sol_candidates) == 1:
        return os.path.join(contract_addr_dir,sol_candidates.pop()+".sol")
    
    return os.path.join(contract_addr_dir,sol_set.pop()+".sol") # 否则，随便返回一个匹配


etherscan_test_root_path = '/data/disk_16t_2/kailun/smart_contract_centralization/test_contracts/etherscan_token/'
def test_erc20():
    tag = 'etherscan_erc20'
    contractsJson_path = etherscan_test_root_path+'token20/contracts.json'
    contracts_dir = etherscan_test_root_path + 'token20/contracts'
    output_dir = etherscan_test_root_path + 'token20/results_erc20'
    is_clean_env = True
    erc_force = 'erc20'
    etest = EtherscanTest(tag,contractsJson_path,contracts_dir,output_dir,is_clean_env,erc_force)
    etest.run()

def test_erc721():
    tag = 'etherscan_erc721'
    contractsJson_path = etherscan_test_root_path + 'token721/contracts.json'
    contracts_dir = etherscan_test_root_path + 'token721/contracts'
    output_dir = etherscan_test_root_path + 'token721/results_erc721'
    is_clean_env = True
    erc_force = 'erc721'

    etest = EtherscanTest(tag,contractsJson_path,contracts_dir,output_dir,is_clean_env,erc_force)
    etest.run()

def test_erc1155():
    tag = 'etherscan_erc1155'
    contractsJson_path = etherscan_test_root_path + 'token1155/contracts.json'
    contracts_dir = etherscan_test_root_path + 'token1155/contracts'
    output_dir = etherscan_test_root_path + 'token1155/results_erc1155'
    is_clean_env = True
    erc_force = 'erc1155'

    etest = EtherscanTest(tag,contractsJson_path,contracts_dir,output_dir,is_clean_env,erc_force)
    etest.run()

if __name__ == "__main__":
    test_erc20()
    #test_erc721()
    #test_erc1155()