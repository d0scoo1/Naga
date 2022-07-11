import sys
sys.path.append(r"/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga")

from tqdm import tqdm
import time
import json
import os
from multiprocessing import Process,Queue
from naga_test import NagaTest

def producer(q,contracts):
    for c in tqdm(contracts):
        q.put(c)


def consumer(q,proj_dir):
    '''
        Consumer get contracts from the producer, and run naga_test
    '''
    while 1:
        c = q.get()
        if c:
            nagaT = NagaTest(c)
            #try:
            nagaT.local_test()
            #except:
            print('NAGA Error:',nagaT.sol_dir,nagaT.sol_file)

            # Record the contract has been tested.
            with open(os.path.join(proj_dir,'contracts_tested',c['address']),'w') as f:
                pass
        else:
            break

def _load_contractsJson(proj_dir,erc_force):

    contracts_tested = os.listdir(os.path.join(proj_dir,'contracts_tested'))
    print('contracts_tested',len(contracts_tested))

    contracts_info = []
    with open(os.path.join(proj_dir,'contracts_info.json'), 'r') as fr:
        line = fr.readline()
        while line != '':
            contracts_info.append(json.loads(line))
            line = fr.readline()
    fr.close()

    contracts = []
    for c in contracts_info:
        if c['address'] in contracts_tested or c['compiler'].startswith('0.4.'):
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

root_dir = ''
def run(proj_dir,erc_force=None,process_num = 4):
    output_dir = os.path.join(proj_dir,'naga_results')
    contracts_tested_dir = os.path.join(output_dir,'contracts_tested')
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    if not os.path.exists(contracts_tested_dir): os.makedirs(contracts_tested_dir)
    
    contracts = _load_contractsJson(proj_dir,erc_force)

    q = Queue(process_num)
    p = Process(target=producer,args=(q,contracts,))
    consumers = [Process(target=consumer,args=(q,proj_dir,)) for i in range(process_num)]

    tasks = [p] + consumers
    [t.start() for t in tasks]
    p.join()
    for i in range(process_num): # If the queue is not empty, we should put a None to tell the consumer to stop
        q.put(None)

root_path = '/mnt/c/Users/vk/Desktop/naga_test'
def erc20_start():
    erc_force  = 'erc20'
    erc_base_path = os.path.join(root_path,'token_tracker',erc_force)
    run(erc_base_path,erc_force)

def erc721_start():
    erc_force  = 'erc721'
    erc_base_path = os.path.join(root_path,'token_tracker',erc_force)
    run(erc_base_path,erc_force)

def erc1155_start():
    erc_force  = 'erc1155'
    erc_base_path = os.path.join(root_path,'token_tracker',erc_force)
    run(erc_base_path,erc_force)

def mainnet_start():
    erc_force  = None
    erc_base_path = os.path.join(root_path,'mainnet')
    run(erc_base_path,erc_force)


def mark():
    rs1 = os.listdir("/mnt/c/Users/vk/Desktop/naga_test/mainnet/results")
    rs2 = os.listdir("/mnt/c/Users/vk/Desktop/naga_test/mainnet/etherscan-contracts")
    with open('/mnt/c/Users/vk/Desktop/naga_test/mainnet/tested_contracts.txt','w') as f:
        pass
    for r in tqdm(list(set(rs1 + rs2))):
        with open('/mnt/c/Users/vk/Desktop/naga_test/mainnet/tested_contracts.txt','a') as f:
            f.write(r[:42]+'\n')


if __name__ == "__main__":
    erc20_start()