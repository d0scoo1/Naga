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


def consumer(q,tested_contracts_path):
    '''
        Consumer get contracts from the producer, and run naga_test
    '''
    while 1:
        c = q.get()
        if c:
            nagaT = NagaTest(c)
            try:
                nagaT.local_test()
            except:
                print('NAGA Error:',nagaT.sol_dir,nagaT.sol_file)

            # Record the contract has been tested.
            with open(tested_contracts_path,'a') as f:
                f.write(c['address']+'\n')
        else:
            break

def _load_contractsJson(contractsJson_path,export_dir,erc_force,output_dir,tested_contracts_path):

    contracts_tested = set()
    with open(tested_contracts_path,'r') as fr:
        line = fr.readline()
        while line != '':
            contracts_tested.add(line.strip())
            line = fr.readline()
    fr.close()
    print('contracts_tested',len(contracts_tested))

    contractsJson = dict()
    with open(contractsJson_path, 'r') as fr:
        line = fr.readline()
        while line != '':
            c = json.loads(line)
            contractsJson[c['address']] = c
            line = fr.readline()
    fr.close()

    # Use implementation to replace the proxy and remove the contract that has been tested
    no_impl_contracts = []
    contracts = []
    for c in contractsJson.values():
        proxy_address = ''
        if c['Proxy'] == '1':# If the contract is a proxy, we test the implementation contract
            proxy_address = c['address']
            if c['Implementation'] in contractsJson:
                c = contractsJson[c['Implementation']]
            else:
                no_impl_contracts.append(c)
                continue
        if c['address'] in contracts_tested:
            continue
        if c['version'] == 'noSolc' or c['version'].startswith('0.4.'):
            continue
        
        contractInfo ={
            'address': c['address'],
            'name': c['ContractName'],
            'version': c['version'],
            'entry_sol_file': "",
            'slither_compile_cost': 0,
            'naga_test_cost': 0,
            'erc_force':erc_force,
            'proxy_address': proxy_address,
            'export_dir':export_dir,
            'output_file':os.path.join(output_dir,c['address'])
        }
        contracts.append(contractInfo)
    
    print('no_impl_contracts',len(no_impl_contracts))
    return contracts



def run(contractsJson_path,export_dir,erc_force,output_dir,process_num = 10):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    tested_contracts_path = os.path.join(export_dir,'naga_tested.txt')
    
    if not os.path.exists(tested_contracts_path):
        with open(tested_contracts_path,'w') as f:
            pass

    contracts = _load_contractsJson(contractsJson_path,export_dir,erc_force,output_dir,tested_contracts_path)

    q = Queue(process_num)
    p = Process(target=producer,args=(q,contracts,))
    consumers = [Process(target=consumer,args=(q,tested_contracts_path,)) for i in range(process_num)]

    tasks = [p] + consumers
    [t.start() for t in tasks]
    p.join()
    for i in range(process_num): # If the queue is not empty, we should put a None to tell the consumer to stop
        q.put(None)

root_path = '/mnt/c/Users/vk/Desktop/naga_test'
def erc20_start():
    erc_force  = 'erc20'
    erc_base_path = os.path.join(root_path,'token_tracker',erc_force)
    contractsJson_path = os.path.join(erc_base_path,'contracts.json')
    export_dir = os.path.join(erc_base_path,'etherscan-contracts')
    output_dir = os.path.join(erc_base_path,'naga_results')
    run(contractsJson_path,export_dir,erc_force,output_dir)

def erc721_start():
    erc_force  = 'erc721'
    erc_base_path = os.path.join(root_path,'token_tracker',erc_force)
    contractsJson_path = os.path.join(erc_base_path,'contracts.json')
    export_dir = os.path.join(erc_base_path,'etherscan-contracts')
    output_dir = os.path.join(erc_base_path,'naga_results')
    run(contractsJson_path,export_dir,erc_force,output_dir)

def erc1155_start():
    erc_force  = 'erc1155'
    erc_base_path = os.path.join(root_path,'token_tracker',erc_force)
    contractsJson_path = os.path.join(erc_base_path,'contracts.json')
    export_dir = os.path.join(erc_base_path,'etherscan-contracts')
    output_dir = os.path.join(erc_base_path,'naga_results')
    run(contractsJson_path,export_dir,erc_force,output_dir)

def mainnet_start():
    erc_force  = None
    contractsJson_path = os.path.join(root_path,'contracts.json')
    export_dir = os.path.join(root_path,'etherscan-contracts')
    output_dir = os.path.join(root_path,'naga_results')
    run(contractsJson_path,export_dir,erc_force,output_dir)


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