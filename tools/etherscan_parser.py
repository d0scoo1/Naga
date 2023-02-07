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

    filename = os.path.join(export_dir, f"{addr}_{contract_name}.sol")

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
        if filename.startswith("/") or filename.startswith("http"):
            if "contracts" in path_filename.parts and not filename.startswith("@"):
                path_filename = Path(*path_filename.parts[path_filename.parts.index("contracts") :])
            else:
                path_filename = Path(filename.split("/")[-1])
        filtered_paths.append(str(path_filename))
        path_filename = Path(directory, path_filename)

        if not os.path.exists(path_filename.parent):
            os.makedirs(path_filename.parent)
        with open(path_filename, "w", encoding="utf8") as file_desc:
            file_desc.write(source_code["content"])

    return list(filtered_paths), directory

def EtherscanParser(addr,info_path,output_dir):
    """
    Parse the result from etherscan

    Args:
        contractRaw_path (str): path to the contract
    """

    with open(info_path, "r", encoding="utf8") as f:
        info =  json.loads(f.read())
    
    if not info["message"].startswith("OK") or "result" not in info or info["result"][0]["SourceCode"] == "":
        #raise NoSourceCode("Contract has no public source code")
        return

    result = info["result"][0]
    assert isinstance(result["SourceCode"], str)
    assert isinstance(result["ContractName"], str)
    source_code = result["SourceCode"]
    contract_name = result["ContractName"]

    contracts_dir = os.path.join(output_dir,'contracts')
    try:
        # etherscan might return an object with two curly braces, {{ content }}
        dict_source_code = json.loads(source_code[1:-1])
        filenames, working_dir = _handle_multiple_files(
            dict_source_code, addr, contract_name, contracts_dir
        )
    except JSONDecodeError:
        try:
            # or etherscan might return an object with single curly braces, { content }
            dict_source_code = json.loads(source_code)
            filenames, working_dir = _handle_multiple_files(
                dict_source_code, addr, contract_name, contracts_dir
            )
        except JSONDecodeError:
            filenames = [
                _handle_single_file(source_code, addr, contract_name, contracts_dir)
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

    with open(os.path.join(output_dir,'contracts_info',addr), "a") as f:
        f.write(json.dumps(result) +'\n')

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

def producer(q,raws_dir):
    contracts = os.listdir(raws_dir)
    for c in tqdm(contracts): q.put(c)

def consumer(q,raws_dir,output_dir):
    while 1:
        c = q.get()
        if c:
            try:
                EtherscanParser(c,os.path.join(raws_dir,c),output_dir)
            except Exception:
                pass
        else:
            break

import shutil
def combine_contracts_info(root_dir):
    '''
    After run, combine all the contracts_info into one file
    '''
    print('loading contracts_info')
    contracts_info = []
    for c in tqdm(os.listdir(os.path.join(root_dir,'contracts_info'))):
        with open(os.path.join(root_dir,'contracts_info',c),'r') as f:
            contracts_info.append(f.read())
        f.close()
    shutil.rmtree(os.path.join(root_dir,'contracts_info'))
    
    print('writing contracts_info')
    contracts_info_path = os.path.join(root_dir,'contracts_info.json')
    if os.path.exists(contracts_info_path):
        os.remove(contracts_info_path)
    with open(contracts_info_path, 'w') as f:
        pass
    with open(contracts_info_path, 'a') as f:
        f.writelines(contracts_info)

def run(root_dir,process_num:int = 10):
    print('Parsing...')
    raws_dir = os.path.join(root_dir,'raws')
    contracts_dir = os.path.join(root_dir,'contracts')
    contracts_info_dir = os.path.join(root_dir,'contracts_info')

    if not os.path.exists(contracts_dir): os.makedirs(contracts_dir)
    if not os.path.exists(contracts_info_dir): os.makedirs(contracts_info_dir)

    q = Queue(process_num)
    p = Process(target=producer,args=(q,raws_dir,))
    consumers = [Process(target=consumer,args=(q,raws_dir,root_dir,)) for i in range(process_num)]

    tasks = [p] + consumers
    [t.start() for t in tasks]
    p.join()
    for i in range(process_num): # If the queue is not empty, we should put a None to tell the consumer to stop
        q.put(None)
    
    print('All the consumers are done.')
    print('Combining the contracts_info...')
    combine_contracts_info(root_dir)
    print('Done.')

root_path = 'C:\\Users\\vk\\Desktop\\naga_test'

def start(path):
    run(os.path.join(root_path,path))

def erc20_start():
    run(os.path.join(root_path,'token_tracker','erc20'))

def erc721_start():
    run(os.path.join(root_path,'token_tracker','erc721'))

def erc1155_start():
    run(os.path.join(root_path,'token_tracker','erc1155'))

def mainnet_start():
    run(os.path.join(root_path,'mainnet'))


if __name__ == "__main__":
    #erc20_start()
    #erc721_start()
    erc1155_start()
    #mainnet_start()