import sys
sys.path.append(r"/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga")

from tqdm import tqdm
import time
import json
import os
from multiprocessing import Process,Queue
from naga_test import NagaTest
from naga.core.expansions import contractInfo

def producer(q,contracts):
    '''
        Producer offers the contracts to consumer
        Etherscan free API limit is 5 requests per second
    '''
    for c in tqdm(contracts):
        q.put(c)
        time.sleep(0.20)


def consumer(q,tested_contracts_path):
    '''
        Consumer get the contract from producer, and run naga_test
    '''
    while 1:
        c = q.get()
        if c:
            nagaT = NagaTest(c)
            try:
                nagaT.test()
            except:
                print('NAGA Error:',nagaT.sol_dir,nagaT.sol_file)

            # record this contract has tested.
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
    contracts = []
    for c in contractsJson.values():
        proxy_address = ''
        if c['Proxy'] == '1':# If the contract is a proxy, we test the implementation contract
            proxy_address = c['address']
            if c['Implementation'] in contractsJson:
                c = contractsJson[c['Implementation']]
            else:
                print('Implementation contract not found:',c['address'],c['Implementation'])
                continue
        if c['address'] in contracts_tested:
            continue
        if c['version'] == 'noSolc' or c['version'].startswith('0.4.'):
            continue

        cInfo = contractInfo(c['address'],c['ContractName'],c['version'],export_dir,erc_force,output_dir)
        cInfo['proxy_address'] = proxy_address
        contracts.append(cInfo)
    return contracts

def _load_mainnet_json(contractsJson_path,export_dir,erc_force,output_dir,tested_contracts_path):
    # mainnet contracts have a lot of error, so we use tested_contracts to record the contract that had been tested.
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

    print('contractsJson',len(contractsJson))


    contracts = []
    for c in contractsJson.values():
        if c['address'] in contracts_tested:
            continue
        if c['compiler'].startswith('0.4.'): #c['compiler'] == 'noSolc' or 
            continue
        cInfo = contractInfo(c['address'],c['name'],c['compiler'],export_dir,erc_force,output_dir)
        cInfo['ether_balance'] = c['balance']
        cInfo['txcount'] = c['txcount']
        cInfo['date'] = c['date']
        contracts.append(cInfo)
    return contracts


def run(contractsJson_path,export_dir,erc_force,output_dir,process_num = 10):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    tested_contracts_path = os.path.join(export_dir,'tested_contracts.txt')
    
    if not os.path.exists(tested_contracts_path):
        with open(tested_contracts_path,'w') as f:
            pass

    if erc_force is not None:
        contracts = _load_contractsJson(contractsJson_path,export_dir,erc_force,output_dir,tested_contracts_path)
    else:
        contracts = _load_mainnet_json(contractsJson_path,export_dir,erc_force,output_dir,tested_contracts_path)

    q = Queue(process_num)
    p = Process(target=producer,args=(q,contracts,))
    consumers = [Process(target=consumer,args=(q,tested_contracts_path,)) for i in range(process_num)]

    tasks = [p] + consumers
    [t.start() for t in tasks]
    p.join()
    for i in range(process_num): # If the queue is not empty, we should put a None to tell the consumer to stop
        q.put(None)

def run_erc20():
    contractsJson_path = "/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga/tests/contract_json/contracts_20.json"

    export_dir = '/mnt/c/Users/vk/Desktop/naga_test/token_tracker/erc20'
    erc_force  = 'erc20'
    output_dir = os.path.join(export_dir,'results')

    run(contractsJson_path,export_dir,erc_force,output_dir)

def run_erc721():
    contractsJson_path = "/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga/tests/contract_json/contracts_721.json"

    export_dir = '/mnt/c/Users/vk/Desktop/naga_test/token_tracker/erc721'
    erc_force  = 'erc721'
    output_dir = os.path.join(export_dir,'results')

    run(contractsJson_path,export_dir,erc_force,output_dir)

def run_erc1155():
    #Implementation: 0x142fd5b9d67721efda3a5e2e9be47a96c9b724a4 是 1529 个合约的实现
    # erc 1155

    contractsJson_path = "/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga/tests/contract_json/contracts_1155.json"

    export_dir = '/mnt/c/Users/vk/Desktop/naga_test/token_tracker/erc1155'
    erc_force  = 'erc1155'
    output_dir = os.path.join(export_dir,'results')

    run(contractsJson_path,export_dir,erc_force,output_dir)

def run_mainnet():

    contractsJson_path = "/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga/tests/contract_json/contracts_mainnet.json"

    export_dir = '/mnt/c/Users/vk/Desktop/naga_test/mainnet'
    erc_force  = None
    output_dir = os.path.join(export_dir,'results')

    run(contractsJson_path,export_dir,erc_force,output_dir)

if __name__ == "__main__":
    #run_erc20()
    #run_erc1155()
    #run_erc721()
    run_mainnet()