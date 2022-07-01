import sys
sys.path.append(".")
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

if __name__ == "__main__":
    #test_erc20()
    test_erc721()