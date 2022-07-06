import sys
sys.path.append(r"/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga")

import os
from slither import Slither
from naga.naga import Naga,nagaInfo
from crytic_compile import CryticCompile,compile_all,is_supported
from crytic_compile.platform.all_platforms import Etherscan,Solc
from crytic_compile.platform.exceptions import InvalidCompilation
from slither.exceptions import SlitherError
from multiprocessing import Process,Queue
from tqdm import tqdm
import time
import json
import logging
from common_sol_file import CommonSolFile

logging.getLogger("CryticCompile").level = logging.CRITICAL

etherscan_api_key= '68I2GBGUU79X6YSIMA8KVGIMYSKTS6UDPI'
solc_dir = '/mnt/c/Users/vk/Desktop/naga/solc/'

export_dir ="/mnt/c/Users/vk/Desktop/naga/"
export_dir_len = len(export_dir)

output_dir = '/mnt/c/Users/vk/Desktop/naga/naga_test'

def naga_test(contract,erc_force = None, attemp = 0):
    contract_address = contract['address']
    contract_name = contract['name']
    contract_version = contract['version']
    compiler = solc_dir +'solc-'+ contract_version
    
    # if the file has downloaded, we directly use it
    sol_dir = os.path.join(export_dir, contract_address + '-' +contract_name)
    sol_file = sol_dir + '.sol'
    if os.path.exists(sol_file):
        slither = Slither(CryticCompile(CommonSolFile(sol_file),solc = compiler,compiler_version=contract_version),disable_solc_warnings = True)
    elif os.path.exists(sol_dir):
        slither = Slither(CryticCompile(CommonSolFile(sol_dir),solc = compiler,compiler_version=contract_version),disable_solc_warnings = True)
    else:
        try:
            slither = Slither(CryticCompile(Etherscan(contract_address,disable_solc_warnings = True),solc = compiler,etherscan_only_source_code = True,etherscan_api_key=etherscan_api_key,export_dir =export_dir))
            return slither
        except InvalidCompilation: # If throw InvalidCompilation, we try again
            if attemp < 3:
                time.sleep(0.1)
                return naga_test(contract,erc_force,attemp+1)
    
    naga = Naga(slither)
    for c in naga.entry_contracts:
        c.detect(erc_force=erc_force)
        entry_sol_file = c.contract.source_mapping['filename_used'][export_dir_len:] # If a contract has multiple solidity files, we should find the entry contract
        naga.set_info(nagaInfo(contract_address=contract_address,contract_name=contract_name,version=contract_version,entry_sol_file = entry_sol_file))
        c.summary_json(os.path.join(output_dir,contract_address))


def producer(q):
    '''
        Producer offers the contracts to consumer
    '''
    contracts_tested = set(os.listdir(output_dir))
    print('contracts_tested',len(contracts_tested))

    contractsJson_path = "/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga/tests/contracts_1155.json"
    contractsJson = dict()
    with open(contractsJson_path, 'r') as fr:
        line = fr.readline()
        while line != '':
            c = json.loads(line)
            c['name'] = c['ContractName']
            contractsJson[c['address']] = c
            line = fr.readline()
    fr.close()

    # Use implementation to replace the proxy and remove the contract that has been tested
    contracts = []
    for c in contractsJson.values():
        
        if c['Proxy'] == '1':# If the contract is a proxy, we test the implementation contract
            if c['Implementation'] in contractsJson:
                c = contractsJson[c['Implementation']]
            else:
                print('Implementation contract not found:',c['address'],c['Implementation'])
                continue
        if c['address'] in contracts_tested:
            continue
        if c['version'] == 'noSolc' or c['version'].startswith('0.4.'):
            continue
        contracts.append(c)

    for c in tqdm(contracts):
        q.put(c)
        time.sleep(0.21)


def consumer(q):
    '''
        Consumer get the contract from producer, and run naga_test
    '''
    while 1:
        c = q.get()
        if c:
            naga_test(c)
        else:
            time.sleep(0.1)
            break

def run(process_num = 5):
    '''
        Etherscan free API limit is 5 requests per second
    '''
    q = Queue(process_num)
    p = Process(target=producer,args=(q,))
    consumers = [Process(target=consumer,args=(q, )) for i in range(process_num)]

    tasks = [p] + consumers
    [t.start() for t in tasks]

    p.join()

    for i in range(process_num): # If the queue is not empty, we should put a None to tell the consumer to stop
        q.put(None)

if __name__ == "__main__":
    run()