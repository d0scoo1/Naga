import sys
sys.path.append(".")

from naga_test import NagaTest
import os
import json
from solc_utils import set_solc
from slither import Slither
from tqdm import tqdm
from naga.naga import Naga
import time

class MainnetTest(NagaTest):
    def __init__(self, tag, contractsJson_path, contract_dir, output_dir, is_clean_env=False, erc_force=None) -> None:
        super().__init__(tag, contractsJson_path, contract_dir, output_dir, is_clean_env, erc_force)


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
            for contract_sol in os.listdir(version_dir):
                # Skip contracts that have been tested
                if contract_sol in self.contracts_tested: continue
                
                contract_addr = '0x' + contract_sol[:40]
                contract_name = contract_sol[41:-4]
                sol_path = os.path.join(version_dir, contract_sol)

                slither = None
                try:
                    before_slither_compile = time.time()
                    slither = Slither(sol_path)
                    after_slither_compile = time.time()
                    slither_compile_cost = after_slither_compile - before_slither_compile
                    self.slither_compiler_cost += slither_compile_cost
                    self.slither_pass += 1

                    cs = slither.get_contract_from_name(contract_name=contract_name)
                    if len(cs) == 1:
                        slither = None

                    self.not_find_entry_contract += 1
                    self._write_line(self.error_logs,'slither,no contract,'+contract_addr+','+contract_name)
                except:
                    slither = None
                    self._write_line(self.error_logs,'slither,compiler error,'+contract_addr+','+contract_name)
                
                if slither is None: continue

                try:
                    before_naga_analyze = time.time()
                    naga = Naga(slither,contract_addr,contract_name,None,version,contractsJson[contract_addr]['balance'],contractsJson[contract_addr]['txcount'],contractsJson[contract_addr]['date'])
                    for contract in naga.entry_contracts:
                        # if is erc, detect, else skip
                        if not contract.is_erc: continue
                        
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


def test_mainnet():
    tag = 'mainnet'
    contractsJson_path =  'token1155/contracts.json'
    contracts_dir =  'token1155/contracts'
    output_dir =  'token1155/results_mainnet'
    is_clean_env = True
    erc_force = None

    mtest = MainnetTest(tag,contractsJson_path,contracts_dir,output_dir,is_clean_env,erc_force)
    mtest.run()

if __name__ == "__main__":
    test_mainnet()
