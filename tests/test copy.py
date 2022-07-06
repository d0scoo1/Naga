
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
export_dir ="/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga/tests"

prefix_dir_len = len(os.path.join(export_dir,)) + 1
solc_dir = '/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga/solc/'

output_dir  = '/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga/tests/result_1155/'


def naga_test_etherscan_first(contract, attempt = 0):
    contract_address = contract['address']
    contract_name = contract['name']
    contract_version = contract['version']
    compiler = solc_dir +'solc-'+ contract_version

    try:
        slither = Slither(CryticCompile(Etherscan(contract_address,disable_solc_warnings = True),solc = compiler,etherscan_only_source_code = True,etherscan_api_key=etherscan_api_key,export_dir =export_dir,etherscan_export_dir =etherscan_export_dir))
    except InvalidCompilation:
        sol_dir = os.path.join(export_dir, etherscan_export_dir, contract_address + '-' +contract_name)
        sol_file = sol_dir + '.sol'

        if os.path.exists(sol_file):
            slither = Slither(CryticCompile(CommonSolFile(sol_file),solc = compiler,compiler_version=contract_version),disable_solc_warnings = True)
        elif os.path.exists(sol_dir):
            slither = Slither(CryticCompile(CommonSolFile(sol_dir),solc = compiler,compiler_version=contract_version),disable_solc_warnings = True)
        else:
            if attempt < 3: # We try to download again, max 5 times
                time.sleep(0.1)
                naga_test_etherscan_first(contract, attempt + 1)
        return

    naga = Naga(slither)
    for c in naga.entry_contracts:
        c.detect(erc_force='erc20')
        entry_sol_file = c.contract.source_mapping['filename_used'] # If a contract has multiple solidity files, we should find the entry contract
        naga.set_info(nagaInfo(contract_address=contract_address,contract_name=contract_name,version=contract_version,entry_sol_file = entry_sol_file))
        c.summary_json(output_dir+contract_address)
        #print(contract_address,c.is_erc)

def naga_test_local_first(contract, attempt = 0):

    contract_address = contract['address']
    contract_name = contract['name']
    contract_version = contract['version']
    compiler = solc_dir +'solc-'+ contract_version

    # if the file has downloaded, we directly use it
    sol_dir = os.path.join(export_dir, etherscan_export_dir, contract_address + '-' +contract_name)
    sol_file = sol_dir + '.sol'

    if os.path.exists(sol_file):
        slither = Slither(CryticCompile(CommonSolFile(sol_file),solc = compiler,compiler_version=contract_version),disable_solc_warnings = True)
    elif os.path.exists(sol_dir):
        slither = Slither(CryticCompile(CommonSolFile(sol_dir),solc = compiler,compiler_version=contract_version),disable_solc_warnings = True)
    else:
        try:
            slither = Slither(CryticCompile(Etherscan(contract_address,disable_solc_warnings = True),solc = compiler,etherscan_only_source_code = True,etherscan_api_key=etherscan_api_key,export_dir =export_dir,etherscan_export_dir =etherscan_export_dir))
        except InvalidCompilation:
            #if attempt < 3: # We try to download again, max 5 times
            #    time.sleep(0.1)
            #    naga_test(contract, attempt + 1)
            return
    naga = Naga(slither)

    for c in naga.entry_contracts:
        c.detect(erc_force='erc20')
        entry_sol_file = c.contract.source_mapping['filename_used'][prefix_dir_len:] # If a contract has multiple solidity files, we should find the entry contract
        naga.set_info(nagaInfo(contract_address=contract_address,contract_name=contract_name,version=contract_version,entry_sol_file = entry_sol_file))
        c.summary_json(output_dir+contract_address)

        #print(contract_address,c.is_erc)


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
            naga_test_etherscan_first(c)
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

def find_all_sol_files(dir):
    sol_files = []
    for root, dirs, files in os.walk(dir):
        root = root[len(dir):]
        for file in files:
            if file.endswith('.sol'):
                sol_files.append(os.path.join(root, file))
    return sol_files

if __name__ == "__main__":

    #run()
    
    contracts_tested = set(os.listdir(output_dir))
    old_contracts_tested = set(os.listdir('/mnt/c/Users/vk/Desktop/old.results_erc1155/etherscan_erc1155_json'))
    #print(contracts_tested - old_contracts_tested)
    #print(old_contracts_tested - contracts_tested)
    print(len(old_contracts_tested - contracts_tested))

    compiler = solc_dir +'solc-0.8.11'

    slither = Slither(Etherscan("0x0237ef6fda5bccb554e25338817aaef13a88b830",disable_solc_warnings = True),solc = compiler,etherscan_only_source_code = True,etherscan_api_key=etherscan_api_key,export_dir=export_dir)

    #CryticCompile(CommonSolFile("/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga/tests/erc20/0x85eee30c52b0b379b046fb0f85f4f3dc3009afec-KeepToken/contracts"),solc = compiler)
