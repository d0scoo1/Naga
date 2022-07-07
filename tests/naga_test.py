import sys
sys.path.append(r"/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga")

import os
from slither import Slither
from naga.naga import Naga
from naga.core.expansions import ContractExp,contractInfo


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
solc_dir = '/mnt/c/Users/vk/Desktop/naga/solc/'
openzeppelin_dir = '/mnt/c/Users/vk/Desktop/naga/openzeppelin-contracts'


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
    def __init__(self,contract) -> None:
        self.contract = contract
        self.contract_address = contract['address']
        self.contract_name = contract['name']
        self.contract_version = contract['version']
        self.contract_export_dir = contract['export_dir']
        self.erc_force = contract['erc_force']
        self.output_dir = contract['output_dir']

        self.compiler = solc_dir +'solc-'+ self.contract_version
        self.sol_dir = os.path.join(self.contract_export_dir,"etherscan-contracts", self.contract_address + '-' +self.contract_name)
        self.sol_file = self.sol_dir + '.sol'

        self.compile_type = None

        self.max_attemp = 3
        self.time_sleep_second = 0.1

    
    def _local_compile(self):
        if os.path.exists(self.sol_file):
                self.compile_type = 'sol_file'
                return Slither(self.sol_file,solc = self.compiler,disable_solc_warnings = True,solc_remaps = get_solc_remaps(self.contract_version))
        if os.path.exists(self.sol_dir):
            self.compile_type = 'sol_dir'
            return Slither(CryticCompile(MultiSolFiles(self.sol_dir,solc_remaps = get_solc_remaps(self.contract_version)),solc = self.compiler,compiler_version=self.contract_version),disable_solc_warnings = True)

    def _etherscan_download_compile(self):
        self.compile_type = 'etherscan_download'
        return Slither(CryticCompile(Etherscan(self.contract_address,disable_solc_warnings = True),solc = self.compiler,solc_remaps = get_solc_remaps(self.contract_version),etherscan_only_source_code = True,etherscan_api_key=etherscan_api_key,export_dir =self.contract_export_dir))


    def get_slither(self,attemp = 0):
        slither = None
        try:
            slither = self._local_compile()
        except:
            pass

        if slither is not None:
            return slither

        try:
            return self._etherscan_download_compile()
        except: # : If throw InvalidCompilation, we try again
            if attemp < self.max_attemp:
                time.sleep(self.time_sleep_second)
                return self.get_slither(attemp +1)
            return None
    
    def test(self):

        slither = self.get_slither()

        if slither is None:
            return
        
        etherscan_contracts = os.path.join(self.contract_export_dir,"etherscan-contracts")
        export_dir_len = len(etherscan_contracts) + 1

        naga = Naga(slither,contract_name= self.contract_name)
        if len(naga.entry_contracts) == 0: return None
        naga_contract = naga.entry_contracts[0]

 
        if self.erc_force != None:
            naga_contract.detect(erc_force= self.erc_force)
        elif naga_contract.is_erc:
            naga_contract.detect()
        else:
            return None

        self.contract['entry_sol_file']= naga_contract.contract.source_mapping['filename_used'][export_dir_len:]# If a contract has multiple solidity files, we should find the entry contract
        naga_contract.set_info(self.contract)

        output_file = None
        if self.output_dir is not None:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            output_file = os.path.join(self.output_dir,self.contract_address)
        naga_contract.summary_json(output_file)
        return naga_contract


if __name__ == "__main__":

    address= '0xe0c05ec44775e4ad62cdc2eecdf337aa7a143363'
    name= 'Mancium'
    version= '0.8.11'
    export_dir= '/mnt/c/Users/vk/Desktop/naga/naga_test/token_tracker/erc20'
    erc_force= 'erc721'
    output_dir = None
    contract = contractInfo(address,name,version,export_dir,erc_force,output_dir)

    nagaT = NagaTest(contract)
    #nagaT._etherscan_download_compile()
    nagaT._local_compile()


    c = nagaT.test()
    print(c.summary_json())
    for c in c.label_svars_dict['owners']:
        print(c)
    
    #print(nagaT.compile_type)
