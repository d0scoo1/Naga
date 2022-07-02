import sys
sys.path.append(".")
from solc_utils import set_solc
from slither import Slither
from naga.naga import Naga
from naga_test import NagaTest

def test_erc20():
    tag = 'etherscan_erc20'
    contractsJson_path = '/mnt/c/users/vk/naga/tokens/token20/contracts.json'
    contracts_dir = '/mnt/c/users/vk/naga/tokens/token20/contracts'
    output_dir = '/mnt/c/users/vk/naga/tokens/token20/results_erc20'
    is_clean_env = True
    erc_force = 'erc20'
    nagaT = NagaTest(tag,contractsJson_path,contracts_dir,output_dir,is_clean_env,erc_force)
    nagaT.run()

def test_erc721():
    tag = 'etherscan_erc721'
    contractsJson_path = '/mnt/c/users/vk/naga/tokens/token721/contracts.json'
    contracts_dir = '/mnt/c/users/vk/naga/tokens/token721/contracts'
    output_dir = '/mnt/c/users/vk/naga/tokens/token721/results_erc721'
    is_clean_env = True
    erc_force = 'erc721'

    nagaT = NagaTest(tag,contractsJson_path,contracts_dir,output_dir,is_clean_env,erc_force)
    nagaT.run()

def test_erc1155():
    tag = 'etherscan_erc1155'
    contractsJson_path = '/mnt/c/users/vk/naga/tokens/token1155/contracts.json'
    contracts_dir = '/mnt/c/users/vk/naga/tokens/token1155/contracts'
    output_dir = '/mnt/c/users/vk/naga/tokens/token1155/results_erc1155'
    is_clean_env = True
    erc_force = 'erc1155'

    nagaT = NagaTest(tag,contractsJson_path,contracts_dir,output_dir,is_clean_env,erc_force)
    nagaT.run()

def test_one():
    set_solc('0.5.12')
    sol_file = '/mnt/c/users/vk/naga/tokens/token20/contracts/0.5.12/0x5d3a536e4d6dbd6114cc1ead35777bab948e3643/CErc20Delegator.sol'
    print(sol_file)
    slither = Slither(sol_file)
    naga = Naga(slither,'CErc20Delegator','0x312ca0592a39a5fa5c87bb4f1da7b77544a91b87','erc20','0.5.12')

    for c in naga.entry_contracts:
        c.detect()
        for svar in c.label_svars_dict['owners']:
            print(svar)

        print(c.summary_json())

if __name__ == "__main__":
    #test_erc20()
    #test_erc721()
    test_one()