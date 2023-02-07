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
from multiprocessing import Process,Queue
from tqdm import tqdm
import time

etherscan_api_key= '68I2GBGUU79X6YSIMA8KVGIMYSKTS6UDPI'

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

class RateLimitExceeded(Exception): ...
class RequestFail(Exception): ...
class NoSourceCode(Exception): ...

class ContractDownloader():
    def __init__(self, network: str, api_key: str, export_dir: str,):
        self.network = network
        self.api_key = api_key
        self.prefix = SUPPORTED_NETWORK[network][0]
        self.etherscan_url = ETHERSCAN_BASE % (self.prefix, api_key)
        self.export_dir = export_dir
        self.raws_dir = os.path.join(export_dir, 'raws')

        if not os.path.exists(self.raws_dir):
            os.makedirs(self.raws_dir)


    def safe_save(self, addr: str):
        try:
            self.save(addr)
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

    def save(self,addr):
        url = self.etherscan_url + f"&address={addr}"
        with urllib.request.urlopen(url) as response:
            html = response.read()
        info = json.loads(html.decode('utf-8'))

        if "result" in info and info["result"] == "Max rate limit reached":
            raise RateLimitExceeded("Etherscan API rate limit exceeded") #

        if "message" not in info:
            raise RequestFail("Incorrect etherscan request")

        with open(os.path.join(self.raws_dir, addr), 'w') as fw:
            fw.write(json.dumps(info))
        fw.close()

        return info

    def load_requested_contracts(self):
        contracts = set(os.listdir(self.raws_dir))
        return contracts

    def load_implementations(self):
        implementations = set()
        for c in tqdm(os.listdir(self.raws_dir)):
            with open(os.path.join(self.raws_dir, c), 'r') as f:
                info = json.loads(f.read())
                result = info["result"][0]
                if result["Proxy"] == "1" and result["Implementation"] != "":
                    implementations.add(result["Implementation"])

        return implementations

def _load_lines(path):
    contracts = set()
    with open(path,'r') as fr:
        line = fr.readline()
        while line != '':
            contracts.add(line.strip())
            line = fr.readline()
    fr.close()
    return contracts

def _load_contractsJson(contractsJson_path):
    contracts = set()
    with open(contractsJson_path, 'r') as fr:
        line = fr.readline()
        while line != '':
            c = json.loads(line)
            contracts.add(c['address'])
            line = fr.readline()
    fr.close()
    return contracts

def producer(q,contracts):
    '''
    Producer offers the contracts to consumer
    Etherscan free API limit is 5 requests per second
    '''
    for c in tqdm(contracts):
        q.put(c)
        time.sleep(0.20)
    
def consumer(q,downloader):
    '''
    Consumer downloads the contracts
    '''
    while 1:
        c = q.get()
        if c:
            try:
                downloader.safe_save(c)
            except Exception as e:
                print(e)
                if isinstance(e, URLError):
                    return
        else:
            break
    
def run(contracts: List[str],downloader,process_num:int = 10):
    q = Queue(process_num)
    p = Process(target=producer,args=(q,contracts,))
    consumers = [Process(target=consumer,args=(q,downloader,)) for i in range(process_num)]

    tasks = [p] + consumers
    [t.start() for t in tasks]
    p.join()
    for i in range(process_num): # If the queue is not empty, we should put a None to tell the consumer to stop
        q.put(None)

def start(contracts, export_dir, process_num: int = 10):
    print(export_dir)
    downloader = ContractDownloader("mainnet", etherscan_api_key, export_dir)

    print('Contracts downloading...')
    request_contracts = downloader.load_requested_contracts()
    contracts = contracts - request_contracts
    run(contracts,downloader,process_num)

    # Request the implementation
    print('Implementations downloading...')
    contracts_implementation = downloader.load_implementations() - contracts - request_contracts
    run(contracts_implementation,downloader,process_num)
    print('Finish')

#root_path = "/mnt/c/Users/vk/Desktop/naga_test/"
root_path = "C:\\Users\\vk\\Desktop\\naga_test"

def erc_start(erc):
    export_dir = os.path.join(root_path,"token_tracker",erc)
    contracts = _load_contractsJson( os.path.join(export_dir,"htmls.json"))
    start(contracts, export_dir, process_num=10)

def erc20_start():
    erc_start('erc20')

def erc721_start():
    erc_start('erc721')

def erc1155_start():
    erc_start('erc1155')

def mainnet_start():
    export_dir = os.path.join(root_path,"mainnet")
    contracts = _load_contractsJson(os.path.join(root_path,"mainnet","contracts_mainnet.json"))
    start(contracts, export_dir, process_num=10)

def test_one():
    cd = ContractDownloader(network="mainnet", api_key=etherscan_api_key, export_dir="/mnt/c/Users/vk/Desktop/naga_test/tt")
    cd.save('0xdAC17F958D2ee523a2206206994597C13D831ec7')

if __name__ == "__main__":
    #erc20_start()
    #erc721_start()
    #erc1155_start()
    #mainnet_start()
    pass
