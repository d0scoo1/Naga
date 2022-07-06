from re import S
import sys
from telnetlib import PRAGMA_HEARTBEAT
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
from multiple_sol_files import MultiSolFiles

logging.getLogger("CryticCompile").level = logging.CRITICAL

etherscan_api_key= '68I2GBGUU79X6YSIMA8KVGIMYSKTS6UDPI'
solc_dir = '/mnt/c/Users/vk/Desktop/naga/solc/'

export_dir ="/mnt/c/Users/vk/Desktop/naga/"
etherscan_contracts = os.path.join(export_dir,"etherscan-contracts")
export_dir_len = len(etherscan_contracts) + 1

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


def get_slither(contract,erc_force = None, attemp = 0):
    
    contract_address = contract['address']
    contract_name = contract['name']
    contract_version = contract['version']
    compiler = solc_dir +'solc-'+ contract_version
    
    # if the file has downloaded, we directly use it
    sol_dir = os.path.join(etherscan_contracts, contract_address + '-' +contract_name)
    sol_file = sol_dir + '.sol'

    try:
        if os.path.exists(sol_file):
            return Slither(sol_file,solc = compiler,disable_solc_warnings = True,solc_remaps = get_solc_remaps(contract['version']))
        if os.path.exists(sol_dir):
            return Slither(CryticCompile(MultiSolFiles(sol_dir,solc_remaps = get_solc_remaps(contract['version'])),solc = compiler,compiler_version=contract_version),disable_solc_warnings = True)
    except:
        pass

    try:
        return Slither(CryticCompile(Etherscan(contract_address,disable_solc_warnings = True),solc = compiler,solc_remaps = get_solc_remaps(contract['version']),etherscan_only_source_code = True,etherscan_api_key=etherscan_api_key,export_dir =export_dir))
    except: # : If throw InvalidCompilation, we try again
        if attemp < 3:
            time.sleep(0.1)
            return get_slither(contract,erc_force,attemp+1)



def naga_test(contract,output_dir,erc_force = None):
    
    contract_address = contract['address']
    contract_name = contract['name']
    contract_version = contract['version']
    
   
    slither = get_slither(contract,erc_force)
    if slither is None:
        return
    naga = Naga(slither,contract_name= contract_name)
    for c in naga.entry_contracts:
        if erc_force != None:
            c.detect(erc_force=erc_force)
        elif c.is_erc:
            c.detect()
        else:
            continue

        entry_sol_file = c.contract.source_mapping['filename_used'][export_dir_len:] # If a contract has multiple solidity files, we should find the entry contract
        naga.set_info(nagaInfo(contract_address=contract_address,contract_name=contract_name,version=contract_version,entry_sol_file = entry_sol_file))

        output_file = None 
        if output_dir is not None:
            output_file = os.path.join(output_dir,contract_address)
        c.summary_json(output_file)



def producer(q,contracts):
    '''
        Producer offers the contracts to consumer
    '''
    for c in tqdm(contracts):
        q.put(c)
        time.sleep(0.21)


def consumer(q,output_dir,erc_force):
    '''
        Consumer get the contract from producer, and run naga_test
    '''
    while 1:
        c = q.get()
        if c:
            try:
                naga_test(c,output_dir,erc_force)
            except:
                sol_dir = os.path.join(etherscan_contracts, c['address'] + '-' +c['name'])
                sol_file = sol_dir + '.sol'
                print('NAGA Error:',sol_dir,sol_file)
        else:
            time.sleep(0.1)
            break


def _load_contractsJson(contractsJson_path,output_dir):
    contracts_tested = set(os.listdir(output_dir))
    print('contracts_tested',len(contracts_tested))
    #contracts_tested = set()

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
    return contracts

def _load_mainnet_json(contractsJson_path,output_dir):
    contracts_tested = set(os.listdir(output_dir))
    print('contracts_tested',len(contracts_tested))

    contractsJson = dict()
    with open(contractsJson_path, 'r') as fr:
        line = fr.readline()
        while line != '':
            c = json.loads(line)
            c['version'] = c['compiler']
            contractsJson[c['address']] = c
            line = fr.readline()
    fr.close()

    contracts = []
    for c in contractsJson.values():
        if c['address'] in contracts_tested:
            continue
        if c['version'] == 'noSolc' or c['version'].startswith('0.4.'):
            continue
        contracts.append(c)
    return contracts


def run(contractsJson_path,output_dir,erc_force,process_num = 5):
    '''
        Etherscan free API limit is 5 requests per second
    '''

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if erc_force is not None:
        contracts = _load_contractsJson(contractsJson_path,output_dir)
    else:
        contracts = _load_mainnet_json(contractsJson_path,output_dir)

    q = Queue(process_num)
    p = Process(target=producer,args=(q,contracts,))
    consumers = [Process(target=consumer,args=(q,output_dir,erc_force,)) for i in range(process_num)]

    tasks = [p] + consumers
    [t.start() for t in tasks]
    p.join()
    for i in range(process_num): # If the queue is not empty, we should put a None to tell the consumer to stop
        q.put(None)

def run_erc20():
    erc_force = 'erc20'
    contractsJson_path = "/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga/tests/contract_json/contracts_20.json"
    output_dir = '/mnt/c/Users/vk/Desktop/naga/naga_test/erc20'
    run(contractsJson_path,output_dir,erc_force)

def run_erc721():
    erc_force = 'erc721'
    contractsJson_path = "/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga/tests/contract_json/contracts_721.json"
    output_dir = '/mnt/c/Users/vk/Desktop/naga/naga_test/erc721'
    run(contractsJson_path,output_dir,erc_force)

def run_erc1155():
    #Implementation: 0x142fd5b9d67721efda3a5e2e9be47a96c9b724a4 是 1529 个合约的实现
    # erc 1155
    erc_force = 'erc1155'
    contractsJson_path = "/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga/tests/contract_json/contracts_1155.json"
    output_dir = '/mnt/c/Users/vk/Desktop/naga/naga_test/erc1155'
    run(contractsJson_path,output_dir,erc_force)

def run_mainnet():
    erc_force = None
    contractsJson_path = "/mnt/d/onedrive/sdu/Research/centralization_in_blackchain/naga/tests/contract_json/contracts_mainnet.json"
    output_dir = '/mnt/c/Users/vk/Desktop/naga/naga_test/mainnet'
    run(contractsJson_path,output_dir,erc_force)

if __name__ == "__main__":
    run()

    contract = {
        'address':'0x75442Ac771a7243433e033F3F8EaB2631e22938f',
        'name':'Comptroller',
        'version':'0.5.16',
    }
    erc_force='erc1155'

    compiler = solc_dir +'solc-'+ contract['version']

    contract_address = contract['address']
    contract_name = contract['name']
    contract_version = contract['version']
    
    # if the file has downloaded, we directly use it
    sol_dir = os.path.join(etherscan_contracts, contract_address + '-' + contract_name)
    sol_file = sol_dir + '.sol'
    #print(sol_dir,sol_file)

    #naga_test(contract,None,)
    #Slither(CryticCompile(MultiSolFiles(sol_dir),solc = compiler,solc_remaps = get_solc_remaps(contract['version']),compiler_version=contract_version,),disable_solc_warnings = True)
    #Slither(CryticCompile(Etherscan(contract['address'],disable_solc_warnings = True),solc =compiler ,etherscan_only_source_code = True,etherscan_api_key=etherscan_api_key,export_dir =export_dir))

    #Slither('/mnt/c/Users/vk/Desktop/naga/etherscan-contracts/0x4c7b456ec8fcb19fb4e6a11a04bc3ec1d71dc1a8-Router/contracts/external/Router.sol',solc = compiler,solc_remaps = get_solc_remaps(contract['version']) )
    #print(get_solc_remaps(contract['version']))