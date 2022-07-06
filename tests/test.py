import sys
sys.path.append(r"/mnt/d/onedrive/sdu/Research/Centralization in Blackchain/naga")

import os
from slither import Slither
from solc_utils import set_solc
from naga.naga import Naga
from crytic_compile import CryticCompile,compile_all
from crytic_compile.platform.etherscan import Etherscan
from crytic_compile.platform.exceptions import InvalidCompilation
def test_one():
    #set_solc('0.4.12')
    #sol_file = '/data/disk_16t_2/kailun/smart_contract_centralization/naga/tests/contracts/HelloERC20.sol'
    #print(sol_file)

    contract_address = '0xB8c77482e45F1F44dE1745F52C74426C631bDD52'
    contract_name = 'BNB'
    etherscan_api_key='68I2GBGUU79X6YSIMA8KVGIMYSKTS6UDPI'
    export_dir ="/mnt/d/onedrive/sdu/Research/Centralization in Blackchain/naga/tests"
    etherscan_export_dir ='erc20'
    try:
        slither = Slither(CryticCompile(Etherscan(contract_address),etherscan_only_source_code = True,etherscan_api_key=etherscan_api_key,export_dir =export_dir,etherscan_export_dir =etherscan_export_dir))
    except InvalidCompilation:
        slither = Slither(os.path.join(export_dir, etherscan_export_dir, contract_address + '-' +contract_name +'.sol'))

    naga = Naga(slither,'0x312ca0592a39a5fa5c87bb4f1da7b77544a91b87',contract_name)

    for c in naga.entry_contracts:
        print(c.is_erc)
        #c.detect()
        #for svar in c.label_svars_dict['owners']:
        #    print(svar)

        #print(c.summary_json())


if __name__ == "__main__":
    test_one()