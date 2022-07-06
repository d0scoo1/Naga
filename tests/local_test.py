from tqdm import tqdm
import time
import json
import os
from slither import Slither
from naga.naga import Naga,nagaInfo

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

def get_naga_test_json(json_path):
    contractsJSON = []
    for jfile in os.listdir(json_path):
        with open(os.path.join(json_path,jfile)) as f:
            contract = json.load(f)
            contractsJSON.append(contract)
        f.close()
    return contractsJSON

def naga_test(contract,output_dir,erc_force = None):
    sol_file = os.path.join(etherscan_contracts,contract['entry_sol_file'])
    compiler = solc_dir +'solc-'+ contract['version']
    
    try:
        slither = Slither(sol_file,solc = compiler,disable_solc_warnings = True,solc_remaps = get_solc_remaps(contract['version']))
    except:
        return

    try:
        naga = Naga(slither,contract_name= contract['name'])
        for c in naga.entry_contracts:
            if erc_force != None:
                c.detect(erc_force=erc_force)
            elif c.is_erc:
                c.detect()
            else:
                continue

            entry_sol_file = c.contract.source_mapping['filename_used'][export_dir_len:] # If a contract has multiple solidity files, we should find the entry contract
            naga.set_info(nagaInfo(contract_address=contract['address'],contract_name= contract['name'],version=contract['version'],entry_sol_file = entry_sol_file))

            output_file = None 
            if output_dir is not None:
                output_file = os.path.join(output_dir,contract['address'])
            c.summary_json(output_file)
    except:
        return

