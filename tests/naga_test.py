import sys
sys.path.append(r"/data/disk_16t_2/kailun/scc/naga")
from slither_compiler import *
import os
import time
from naga.naga import Naga

class NagaTest():
    def __init__(self,contract,input_dir,output_dir) -> None:
        self.contract = contract
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.contracts_dir = os.path.join(input_dir,'contracts')
        self.result_path = os.path.join(output_dir,'results')

    def get_slither(self,):
        sol_dir = os.path.join(self.contracts_dir, self.contract['address'] + '_' + self.contract['name'])
        if os.path.exists(sol_dir):
            return multi_compile(sol_dir,self.contract['compiler'])
        sol_file = sol_dir +'.sol'
        if os.path.exists(sol_file):
            return single_compile(sol_file,self.contract['compiler'])
        
        #return etherscan_download_compile(self.contract['address'],self.contract['name'],self.contract['compiler'],contracts_dir)
        
    def local_test(self):

        try:
            s_start_time = time.time()
            slither = self.get_slither()
            s_end_time = time.time()
            self.contract['slither_compile_cost'] = s_end_time - s_start_time
        except:
            with open(os.path.join(self.output_dir,'errors',self.contract['address']+'_slither'),'w') as f:
                pass
            return

        n_start_time = time.time()
        naga = Naga(slither,contract_name= self.contract['name'])
        if len(naga.entry_contracts) == 0: return
        naga_contract = naga.entry_contracts[0]
        if self.contract['erc_force'] != None:
            naga_contract.detect(erc_force= self.contract['erc_force'])
        elif naga_contract.is_erc:
            naga_contract.detect()
        else:
            return
        n_end_time = time.time()
        self.contract['naga_test_cost'] = n_end_time - n_start_time
        self.contract['entry_sol_file'] = naga_contract.contract.source_mapping['filename_used'][len(self.contracts_dir)+1:]

        naga_contract.set_info(self.contract)
        naga_contract.summary_json(os.path.join(self.result_path,self.contract['address']))
        return naga_contract

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
            try:
                nagaT.local_test()
            except:
                with open(os.path.join(output_dir,'errors',c['address']+'_naga'),'w') as f:
                    pass
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

    contracts = []
    for c in contracts_info:
        if c['address'] in contracts_tested or int(c['compiler'][2]) <= 4:
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
    return contracts

def _count_errors(output_dir):
    errors = []
    slither_errors = []
    for c in os.listdir(os.path.join(output_dir,'errors')):
        if c[43:] == 'naga': errors.append(c[:42])
        else: slither_errors.append(c[:42])
    print('naga errors:',len(errors))
    print('slither errors:',len(slither_errors))

def run(input_dir,output_dir, erc_force = None, process_num = 4):
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

    _count_errors(output_dir)

input_dir = '/home/yankailun/naga_test'
output_dir = '/data/disk_16t_2/kailun/scc/naga_output'
def start(erc_force):
    if erc_force == 'mainnet':
        run(os.path.join(input_dir,'mainnet'),os.path.join(output_dir,erc_force),None)
    else:
        run(os.path.join(input_dir,'token_tracker',erc_force),os.path.join(output_dir,erc_force),None)

if __name__ == "__main__":
    #start('erc20')
    #start('erc721')
    #start('erc1155')
    #start('mainnet')
    pass