import json
import logging
import os
import re
from sys import implementation
import urllib.request
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Union, Tuple, Optional
from urllib.error import URLError
etherscan_api_key= 'IF4W9FY2DA49591MT2CJA3KZDN2I7TPXC5'

ETHERSCAN_BASE = "https://api%s/api?module=contract&action=getsourcecode&apikey=%s"

SUPPORTED_NETWORK = {
    # Key, (prefix_base, perfix_bytecode)
    "mainnet": (".etherscan.io", "etherscan.io"),
    "ropsten": ("-ropsten.etherscan.io", "ropsten.etherscan.io"),
    "kovan": ("-kovan.etherscan.io", "kovan.etherscan.io"),
    "rinkeby": ("-rinkeby.etherscan.io", "rinkeby.etherscan.io"),
    "goerli": ("-goerli.etherscan.io", "goerli.etherscan.io"),
    "tobalaba": ("-tobalaba.etherscan.io", "tobalaba.etherscan.io"),
    "bsc": (".bscscan.com", "bscscan.com"),
    "testnet.bsc": ("-testnet.bscscan.com", "testnet.bscscan.com"),
    "arbi": (".arbiscan.io", "arbiscan.io"),
    "testnet.arbi": ("-testnet.arbiscan.io", "testnet.arbiscan.io"),
    "poly": (".polygonscan.com", "polygonscan.com"),
    "avax": (".snowtrace.io", "snowtrace.io"),
    "testnet.avax": ("-testnet.snowtrace.io", "testnet.snowtrace.io"),
    "ftm": (".ftmscan.com", "ftmscan.com"),
}

def _handle_single_file(
    source_code: str, addr: str, contract_name: str, export_dir: str
) -> str:
    """Handle a result with a single file

    Args:
        source_code (str): source code
        addr (str): contract address
        contract_name (str): contract name
        export_dir (str): directory where the code will be saved

    Returns:
        str: filename containing the source code
    """

    filename = os.path.join(export_dir, f"{addr}-{contract_name}.sol")

    with open(filename, "w", encoding="utf8") as file_desc:
        file_desc.write(source_code)

    return filename


def _handle_multiple_files(
    dict_source_code: Dict, addr: str, contract_name: str, export_dir: str
) -> Tuple[List[str], str]:
    """Handle a result with a multiple files. Generate multiple Solidity files

    Args:
        dict_source_code (Dict): dict result from etherscan
        addr (str): contract address
        contract_name (str): contract name
        export_dir (str): directory where the code will be saved

    Returns:
        Tuple[List[str], str]: filesnames, directory, where target_filename is the main file
    """

    directory = os.path.join(export_dir, f"{addr}_{contract_name}")

    if "sources" in dict_source_code:
        # etherscan might return an object with a sources prop, which contains an object with contract names as keys
        source_codes = dict_source_code["sources"]
    else:
        # or etherscan might return an object with contract names as keys
        source_codes = dict_source_code

    filtered_paths: List[str] = []
    for filename, source_code in source_codes.items():
        path_filename = Path(filename)
        if 'https://' or 'http://' in filename:
            if "contracts" in path_filename.parts and not filename.startswith("@"):
                path_filename = Path(*path_filename.parts[path_filename.parts.index("contracts") :])
            else:
                filename = filename.split("/")[-1]
        filtered_paths.append(str(path_filename))
        path_filename = Path(directory, path_filename)

        if not os.path.exists(path_filename.parent):
            os.makedirs(path_filename.parent)
        with open(path_filename, "w", encoding="utf8") as file_desc:
            file_desc.write(source_code["content"])

    return list(filtered_paths), directory

class RateLimitExceeded(Exception): ...
class RequestFail(Exception): ...
class NoSourceCode(Exception): ...

class ContractDownloader():

    def __init__(self, network: str, api_key: str, export_dir: str, contract_dir = 'etherscan-contracts'):
        self.network = network
        self.api_key = api_key
        self.prefix = SUPPORTED_NETWORK[network][0]
        self.etherscan_url = ETHERSCAN_BASE % (self.prefix, api_key)
        self.export_dir = export_dir
        self.contract_dir = os.path.join(export_dir, contract_dir)
        self.raw_dir = os.path.join(export_dir, 'raw')
        self.contract_json_record_path = os.path.join(export_dir, 'contracts.json')
        self.no_source_code_path = os.path.join(export_dir, 'no_source_code.txt')
        #self.implementation_path = os.path.join(export_dir, 'implementations.txt')

        if not os.path.exists(self.contract_dir):
            os.makedirs(self.contract_dir)
        if not os.path.exists(self.raw_dir):
            os.makedirs(self.raw_dir)

        if not os.path.exists(self.contract_json_record_path):
            with open(self.contract_json_record_path, 'w') as f:
                pass
        if not os.path.exists(self.no_source_code_path):
            with open(self.no_source_code_path, 'w') as f:
                pass
        #if not os.path.exists(self.implementation_path):
        #    with open(self.implementation_path, 'w') as f:
        #        pass
        

    def save(self, addr: str):
        info = self._request_info(addr)
        result = self._request_paser(addr, info)
        self._save_request_raw(addr, info)
        return result
    
    def safe_save(self, addr: str):
        try:
            results = self.save(addr)
            with open(self.contract_json_record_path, 'a') as f:
                f.write(json.dumps(results) + '\n')
        except RequestFail:
            pass
        except NoSourceCode: # Contract has no public source code
            with open(self.no_source_code_path, 'a') as f:
                f.write(addr+'\n')
        except RateLimitExceeded:
            """
            If rate limit exceeded, wait for 0.2 second and try again
            """
            time.sleep(0.2)
            self.safe_save(addr)


    def _request_info(self,addr):
        url = self.etherscan_url + f"&address={addr}"
        with urllib.request.urlopen(url) as response:
            html = response.read()
        return json.loads(html.decode('utf-8'))

    def _request_paser(self,addr,info):

        if "result" in info and info["result"] == "Max rate limit reached":
            raise RateLimitExceeded("Etherscan API rate limit exceeded") #

        if "message" not in info:
            raise RequestFail("Incorrect etherscan request")

        if not info["message"].startswith("OK"):
            raise NoSourceCode("Contract has no public source code")

        if "result" not in info:
            raise NoSourceCode("Contract has no public source code")

        result = info["result"][0]
        assert isinstance(result["SourceCode"], str)
        assert isinstance(result["ContractName"], str)
        source_code = result["SourceCode"]
        contract_name = result["ContractName"]

        if source_code == "":
            raise NoSourceCode("Contract has no public source code")
        
        try:
            # etherscan might return an object with two curly braces, {{ content }}
            dict_source_code = json.loads(source_code[1:-1])
            filenames, working_dir = _handle_multiple_files(
                dict_source_code, addr, contract_name, self.contract_dir
            )
        except JSONDecodeError:
            try:
                # or etherscan might return an object with single curly braces, { content }
                dict_source_code = json.loads(source_code)
                filenames, working_dir = _handle_multiple_files(
                    dict_source_code, addr, contract_name, self.contract_dir
                )
            except JSONDecodeError:
                filenames = [
                    _handle_single_file(source_code, addr, contract_name, self.contract_dir)
                ]

        # Return the contracts.json

        del result['ABI']
        del result['ConstructorArguments']
        #del r['LicenseType']
        del result['SwarmSource']
        del result['SourceCode']
        del result['ContractName']

        result['name'] = contract_name
        result['address'] = addr
        result['compiler'] = re.findall(r"\d+\.\d+\.\d+", _convert_version(result["CompilerVersion"]))[0]

        return result
    
    def _save_request_raw(self,addr,info):
        # Save the request result in the raw directory
        with open(os.path.join(self.raw_dir, addr), 'w') as fw:
            fw.write(json.dumps(info))
        fw.close()

def _convert_version(version: str) -> str:
    """Convert the compiler version

    Args:
        version (str): original version

    Returns:
        str: converted version
    """
    return version[1 : version.find("+")]


from multiprocessing import Process,Queue
from tqdm import tqdm
import time

def producer(q,contracts):
    '''
        Producer offers the contracts to consumer
        Etherscan free API limit is 5 requests per second
    '''
    for c in tqdm(contracts):
        q.put(c)
        time.sleep(0.20)

def consumer(q,contractDownloader):
    while 1:
        c = q.get()
        if c:
            try:
                contractDownloader.safe_save(c)
            except Exception as e:
                print(e)
                break
        else:
            break

def _load_contractsJson(contractsJson_path):
    contracts = []
    with open(contractsJson_path, 'r') as fr:
        line = fr.readline()
        while line != '':
            c = json.loads(line)
            contracts.append(c['address'])
            line = fr.readline()
    fr.close()
    return contracts

def _load_implementations(contractsJson_path):
    implementations = []
    with open(contractsJson_path, 'r') as fr:
        line = fr.readline()
        while line != '':
            c = json.loads(line)
            if c['Proxy'] == '1' and c['Implementation'] != '':
                implementations.append(c['Implementation'])
            line = fr.readline()
    fr.close()
    return implementations

def _load_lines(path):
    contracts = []
    with open(path,'r') as fr:
        line = fr.readline()
        while line != '':
            contracts.append(line.strip())
            line = fr.readline()
    fr.close()
    return contracts

def start(contracts_index_path,export_dir,process_num = 8):

    CDer = ContractDownloader("mainnet", etherscan_api_key, export_dir)

    contracts_requested = set(_load_contractsJson(CDer.contract_json_record_path) 
                            + _load_lines(CDer.no_source_code_path))
    contracts = set(_load_contractsJson(contracts_index_path)) - contracts_requested

    run(contracts,CDer,process_num)

    # Request the implementation
    print('Implementations requesting...')
    contracts_implementation = set(_load_implementations(CDer.contract_json_record_path)) - contracts_requested - contracts
    run(contracts_implementation,CDer,process_num)

    print('Finish')
    
def run(contracts,contractDownloader,process_num = 5):
    q = Queue(process_num)
    p = Process(target=producer,args=(q,contracts,))
    consumers = [Process(target=consumer,args=(q,contractDownloader,)) for i in range(process_num)]

    tasks = [p] + consumers
    [t.start() for t in tasks]
    p.join()
    for i in range(process_num): # If the queue is not empty, we should put a None to tell the consumer to stop
        q.put(None)

#root_path = "/mnt/c/Users/vk/Desktop/naga_test/"
root_path = "C:\\Users\\vk\\Desktop\\naga_test"
def erc20_start():
    export_dir = os.path.join(root_path,"token_tracker","erc20")
    contracts_index_path = os.path.join(export_dir,"htmls.json")
    start(contracts_index_path,export_dir)

def erc721_start():
    export_dir = os.path.join(root_path,"token_tracker","erc721")
    contracts_index_path = os.path.join(export_dir,"htmls.json")
    start(contracts_index_path,export_dir)

def erc1155_start():
    export_dir = os.path.join(root_path,"token_tracker","erc1155")
    contracts_index_path = os.path.join(export_dir,"htmls.json")
    start(contracts_index_path,export_dir)

def mainnet_start():
    contracts_index_path = os.path.join(root_path,"mainnet","contracts_mainnet.json")
    export_dir = os.path.join(root_path,"mainnet")
    start(contracts_index_path,export_dir)

def test_one():
    cd = ContractDownloader(network="mainnet", api_key=etherscan_api_key, export_dir="/mnt/c/Users/vk/Desktop/naga_test/tt")
    try:
        contractJson = cd.save('0xdAC17F958D2ee523a2206206994597C13D831ec7')
        print(contractJson)
    except RequestFail as e:
        print(e[0])

if __name__ == "__main__":
    #erc20_start()
    #erc721_start()
    #erc1155_start()
    mainnet_start()