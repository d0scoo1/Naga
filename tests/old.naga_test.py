import sys
sys.path.append(r"/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga")

import os
from slither import Slither
from naga.naga import Naga
from naga.core.expansions import ContractExp


from crytic_compile import CryticCompile
#from crytic_compile.platform.all_platforms import Etherscan,Solc
from test_platform.multiple_sol_files import MultiSolFiles
from test_platform.etherscan import Etherscan # crytic_compile.platform.Etherscan has bug
from crytic_compile.platform.exceptions import InvalidCompilation

import time
import logging

logging.getLogger("CryticCompile").level = logging.CRITICAL

###### common config ######
etherscan_api_key= '68I2GBGUU79X6YSIMA8KVGIMYSKTS6UDPI'
solc_dir = '/mnt/c/Users/vk/Desktop/naga_test/solc/'
openzeppelin_dir = '/mnt/c/Users/vk/Desktop/naga_test/openzeppelin-contracts'

def get_solc_remaps(version='0.8.0',openzeppelin_dir = openzeppelin_dir):
    '''
    get the remaps for a given solc version
    '''
    v = int(version.split('.')[1])
    if v == 5:
        return "@openzeppelin/=" + openzeppelin_dir + "/openzeppelin-contracts-solc-0.5/"
    if v == 6:
        return "@openzeppelin/=" + openzeppelin_dir + "/openzeppelin-contracts-solc-0.6/"
    if v == 7:
        return "@openzeppelin/=" + openzeppelin_dir + "/openzeppelin-contracts-solc-0.7/"
    if v == 8:
        return "@openzeppelin/=" + openzeppelin_dir + "/openzeppelin-contracts-solc-0.8/"
    return "@openzeppelin/=" + openzeppelin_dir + "/openzeppelin-contracts-solc-0.8/"


class NagaTest():
    def __init__(self,contract,contracts_dir,result_path) -> None:
        self.contract = contract
        self.contract_address = contract['address']
        self.contract_name = contract['name']
        self.contract_compiler = contract['compiler']
        self.erc_force = contract['erc_force']
        self.contracts_dir = contracts_dir
        self.result_path = result_path

        self.compiler = solc_dir +'solc-'+ self.contract_compiler
        self.sol_dir = os.path.join(self.contracts_dir, self.contract_address + '_' +self.contract_name)
        self.sol_file = self.sol_dir +'.sol'

        #self.max_attemp = 3
        #self.time_sleep_second = 0.1

    def local_compile(self):
        print(self.sol_dir,self.sol_file)
        if os.path.exists(self.sol_file):
                return Slither(self.sol_file,solc = self.compiler,disable_solc_warnings = True,solc_remaps = get_solc_remaps(self.contract_compiler))
        if os.path.exists(self.sol_dir):
            return Slither(CryticCompile(MultiSolFiles(self.sol_dir,solc_remaps = get_solc_remaps(self.contract_compiler)),solc = self.compiler,compiler_version=self.contract_compiler),disable_solc_warnings = True)

    def etherscan_download_compile(self):
        return Slither(CryticCompile(Etherscan(self.contract_address,disable_solc_warnings = True),solc = self.compiler,solc_remaps = get_solc_remaps(self.contract_compiler),etherscan_only_source_code = True,etherscan_api_key=etherscan_api_key,export_dir =self.contracts_dir))

    def local_test(self):
        try:
            s_start_time = time.time()
            slither = self.local_compile()
            s_end_time = time.time()
            self.contract['slither_compile_cost'] = s_end_time - s_start_time
        except:
            print('slither compile error',self.contract_address,self.contract_name,self.contract_compiler)
            return

        n_start_time = time.time()
        naga = Naga(slither,contract_name= self.contract_name)
        
        if len(naga.entry_contracts) == 0: return
        naga_contract = naga.entry_contracts[0]
        
        if self.erc_force != None:
            naga_contract.detect(erc_force= self.erc_force)
        elif naga_contract.is_erc:
            naga_contract.detect()
        else:
            return
        n_end_time = time.time()
        self.contract['naga_test_cost'] = n_end_time - n_start_time

        try:
            n_start_time = time.time()
            naga = Naga(slither,contract_name= self.contract_name)
            
            if len(naga.entry_contracts) == 0: return
            naga_contract = naga.entry_contracts[0]
            
            if self.erc_force != None:
                naga_contract.detect(erc_force= self.erc_force)
            elif naga_contract.is_erc:
                naga_contract.detect()
            else:
                return
            n_end_time = time.time()
            self.contract['naga_test_cost'] = n_end_time - n_start_time
        except:
            print('naga test failed',self.contract_address,self.contract_name,self.contract_compiler)
            return

        export_dir_len = len(self.contracts_dir) + 1

        self.contract['entry_sol_file'] = naga_contract.contract.source_mapping['filename_used'][export_dir_len:]# If a contract has multiple solidity files, we should find the entry contract

        contractInfo = self.contract
        del contractInfo['export_dir']
        del contractInfo['result_path']
        naga_contract.set_info(contractInfo)
        naga_contract.summary_json(self.result_path)
        return naga_contract


if __name__ == "__main__":

    contractInfo ={
        'address': '0xd417144312dbf50465b1c641d016962017ef6240',
        'name': 'CovalentQueryToken',
        'compiler':'0.6.2',
        'entry_sol_file': "",
        'slither_compile_cost': 0,
        'naga_test_cost': 0,
        'erc_force': 'erc20',
        #'proxy_address': proxy_address,
        'export_dir':os.path.join('/mnt/c/Users/vk/Desktop/','naga_results'),
        'result_path': None
    }

    nagaT = NagaTest(contractInfo)
    slither = nagaT.local_compile()
    print(slither)
