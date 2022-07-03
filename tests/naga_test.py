import os
import json
from solc_utils import set_solc
from slither import Slither
from tqdm import tqdm
from naga.naga import Naga
import time

"""
    首先我们从 contract_dir 中依次读取每个合约
    然后从 contractsJson 中查询这个合约是否是代理，如果是代理，则跳过。
    如果是 Proxy，我们将只进行标记并跳过
"""

class NagaTest():
    def __init__(self,tag,contractsJson_path,contract_dir,output_dir,is_clean_env = False,erc_force = None) -> None:
        self.tag = tag # test tag
        self.contractsJson_path = contractsJson_path
        self.contract_dir = contract_dir # version/address/contract.sol
        self.output_dir = output_dir
        self.is_clean_env = is_clean_env
        self.erc_force = erc_force

        self.output_json_dir = os.path.join(self.output_dir,self.tag+'_json')
        self.output_csv = os.path.join(self.output_dir,self.tag+'.csv')
        self.output_logs = os.path.join(self.output_dir,self.tag+'.logs')
        self.output_summary = os.path.join(self.output_dir,self.tag+'_summary.log')
        self.error_logs = os.path.join(self.output_dir,self.tag+'_error.logs')
        self.contracts_tested = set()

        self.contract_version_0_4 = 0
        self.contract_num = 0
        self.contract_is_proxy = 0
        self.proxy_has_implement = 0
        self.slither_compiler_error = 0
        self.not_find_entry_contract = 0
        self.naga_test_success = 0
        self.naga_test_fail = 0
        self.naga_erc_20 = 0
        self.naga_erc_721 = 0
        self.naga_erc_1155 = 0
        self.slither_compiler_cost = 0
        self.slither_pass = 0
        self.naga_test_cost = 0
        self.start_time = time.time()
        self.end_time = None
        self.test_cost = 0

        self.init_env()

    def init_env(self):
        if self.is_clean_env:
            self._clean_env()
        if not os.path.exists(self.output_json_dir):
            os.makedirs(self.output_json_dir)

        self.contracts_tested = set()
        for file_name in os.listdir(self.output_json_dir):
            self.contracts_tested.add(file_name)

    def _clean_env(self):
        if os.path.exists(self.output_json_dir):
            os.system('rm -rf '+self.output_json_dir)
        if os.path.exists(self.output_csv):
            os.remove(self.output_csv)
        if os.path.exists(self.output_logs):
            os.remove(self.output_logs)
        if os.path.exists(self.output_summary):
            os.remove(self.output_summary)
        if os.path.exists(self.error_logs):
            os.remove(self.error_logs)
        
    
    def _write_line(self,file,content):
        with open(file,"a") as fw:
            fw.write(content+'\n')
        fw.close()
    
    def _write_json(self,fileName,content):
        with open(os.path.join(self.output_json_dir,fileName),"w") as fw:
            fw.write(content)
        fw.close()

    def _get_entry_contract(self,contract_addr_dir,contract_address,contract_name):
        pass
    
    def run(self):
        pass

    def output_test_summary(self):
        self.end_time = time.time()
        self.test_cost = self.end_time - self.start_time
        txt = ''
        for name,value in vars(self).items():
            if name != "contracts_tested":
                txt += '{:23} : {}\n'.format(name,str(value))
        print(txt)
        self._write_line(self.output_summary,txt)


    def load_contractsJson(self):
        contractsJson = {}
        with open(self.contractsJson_path, 'r') as fr:
            line = fr.readline()
            while line != '':
                c = json.loads(line)
                contractsJson[c['address']] = c
                line = fr.readline()
            fr.close()
        return contractsJson


def count_04_contracts(contract_dir):
    """
        统计 0.4 版本的合约数量
    """
    count = 0
    for version in tqdm(os.listdir(contract_dir)):
            if version.startswith('0.4.'):
                count += len(os.listdir(contract_dir))
    return count