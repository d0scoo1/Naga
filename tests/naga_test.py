import sys
sys.path.append(r"/data/disk_16t_2/kailun/scc/naga")
from slither_compiler import *
import os
import time
from naga.naga import Naga
from func_timeout.exceptions import FunctionTimedOut
from func_timeout import func_set_timeout

time_out_seconds = 10

class NagaTest():
    def __init__(self,contract,input_dir,output_dir) -> None:
        self.contract = contract
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.contracts_dir = os.path.join(input_dir,'contracts')
        self.result_path = os.path.join(output_dir,'results')

    def _get_slither(self):
        sol_dir = os.path.join(self.contracts_dir, self.contract['address'] + '_' + self.contract['name'])
        if os.path.exists(sol_dir):
            #print(sol_dir,self.contract['compiler'])
            return multi_compile(sol_dir,self.contract['compiler'])
        sol_file = sol_dir +'.sol'
        if os.path.exists(sol_file):
            #print(sol_file,self.contract['compiler'])
            return single_compile(sol_file,self.contract['compiler'])

        #return etherscan_download_compile(self.contract['address'],self.contract['name'],self.contract['compiler'],contracts_dir)

    def local_test(self):
        try:
            s_start_time = time.time()
            slither = self._get_slither()
            s_end_time = time.time()
            self.contract['slither_compile_cost'] = s_end_time - s_start_time
        except FunctionTimedOut:
            self._write_error('slither_timeout')
            return
        except:
            self._write_error('slither_compileError')
            return

        try:
            naga_contract = self._naga_test(slither)
        except FunctionTimedOut:
            self._write_error('naga_timeout')
            return
        except:
            self._write_error('naga_error')
            return

        return naga_contract

    @func_set_timeout(time_out_seconds)
    def _naga_test(self,slither):
        n_start_time = time.time()
        naga = Naga(slither,contract_name= self.contract['name'])
        if len(naga.entry_contracts) == 0: 
            self._write_error('naga_noEntryContract')
            return
        naga_contract = naga.entry_contracts[0]
        if self.contract['erc_force'] != None:
            naga_contract.detect(erc_force= self.contract['erc_force'])
        elif naga_contract.is_erc:
            naga_contract.detect()
        else:
            self._write_error('naga_isNotERC')
            return
        n_end_time = time.time()
        self.contract['naga_test_cost'] = n_end_time - n_start_time
        self.contract['entry_sol_file'] = naga_contract.contract.source_mapping['filename_used'][len(self.contracts_dir)+1:]

        naga_contract.set_info(self.contract)
        naga_contract.summary_json(os.path.join(self.result_path,self.contract['address']))
        
        return naga_contract


    def _write_error(self,error_msg):
        '''
        naga_errors: noEntryContract,timeout,isNotERC,error
        slither_errors: timeout,compileError
        '''
        with open(os.path.join(self.output_dir,'errors',self.contract['address']+'_'+error_msg),'w') as f:
                pass

from multiprocessing import Process,Queue
from tqdm import tqdm
import json

def producer(q,contracts):
    for c in tqdm(contracts):
        q.put(c)

def consumer(q,input_dir,output_dir):
    while 1:
        c = q.get()
        if c:
            nagaT = NagaTest(c,input_dir,output_dir)
            
            nagaT.local_test()
            
        else:
            return

def _load_contracts(input_dir,output_dir,erc_force = None):
    # load error contracts & tested contracts
    contracts_tested = os.listdir(os.path.join(output_dir,'results'))
    for c in os.listdir(os.path.join(output_dir,'errors')):
        contracts_tested.append(c[:42])
    contracts_tested = set(contracts_tested)

    contracts_info = []
    with open(os.path.join(input_dir,'contracts_info.json'), 'r') as fr:
        line = fr.readline()
        while line != '':
            contracts_info.append(json.loads(line))
            line = fr.readline()

    staled_contracts = []
    contracts = []
    for c in contracts_info:
        if int(c['compiler'][2]) <= 4:
            staled_contracts.append(c)
            continue
        if c['address'] in contracts_tested:
            continue
        contractInfo ={
            'address': c['address'],
            'name': c['name'],
            'compiler': c['compiler'],
            'entry_sol_file': "",
            'slither_compile_cost': 0,
            'naga_test_cost': 0,
            'erc_force':erc_force,
            'proxy': c['Proxy'],
            'implementation':c['Implementation'],
        }
        contracts.append(contractInfo)
    
    print('contracts_info:',len(contracts_info))
    print('staled_contracts:',len(staled_contracts))

    return contracts

def _count_errors(output_dir):
    naga_errors = []
    naga_not_erc = []
    naga_no_entry = []
    naga_timeout = []
    
    slither_timeout = []
    slither_compileError = []
    for c in os.listdir(os.path.join(output_dir,'errors')):
        if c[43:].startswith('naga'): 
            if c[43:].endswith('isNotERC'):
                naga_not_erc.append(c[:42])
            elif c[43:].endswith('noEntryContract'):
                naga_no_entry.append(c[:42])
            elif c[43:].endswith('timeout'):
                naga_timeout.append(c[:42])
            else:
                naga_errors.append(c[:42])
        else: 
            if c[43:].endswith('timeout'):
                slither_timeout.append(c[:42])
            else:
                slither_compileError.append(c[:42])

    print('naga_errors:',len(naga_errors))
    print('naga_not_erc:',len(naga_not_erc))
    print('naga_no_entry:',len(naga_no_entry))
    print('naga_timeout:',len(naga_timeout))
    print('slither_timeout:',len(slither_timeout))
    print('slither_compileError:',len(slither_compileError))

def run(input_dir,output_dir, erc_force = None, process_num = 50):
    print('input_dir:',input_dir)
    print('output_dir:',output_dir)
    naga_results_dir = os.path.join(output_dir,'results')
    errors_dir = os.path.join(output_dir,'errors')
    if not os.path.exists(naga_results_dir): os.makedirs(naga_results_dir)
    if not os.path.exists(errors_dir): os.makedirs(errors_dir)

    contracts = _load_contracts(input_dir,output_dir,erc_force)

    q = Queue(process_num)
    p = Process(target=producer,args=(q,contracts,))
    consumers = [Process(target=consumer,args=(q,input_dir,output_dir,)) for i in range(process_num)]

    tasks = [p] + consumers
    [t.start() for t in tasks]
    p.join()
    for i in range(process_num): q.put(None)

    print('naga results:', len(os.listdir(naga_results_dir)))
    _count_errors(output_dir)


input_dir = '/home/yankailun/naga_test'
output_dir = '/data/disk_16t_2/kailun/scc/naga_output'
def start(erc_force):
    if erc_force == 'mainnet':
        run(os.path.join(input_dir,'mainnet'),os.path.join(output_dir,erc_force),None)
    else:
        run(os.path.join(input_dir,'token_tracker',erc_force),os.path.join(output_dir,erc_force),erc_force)

if __name__ == "__main__":
    #start('erc20')
    #start('erc721')
    start('erc1155')
    #start('mainnet')
    pass

