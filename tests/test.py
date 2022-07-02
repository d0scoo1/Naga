import sys
sys.path.append(r"/data/disk_16t_2/kailun/smart_contract_centralization/naga")

from solc_utils import set_solc
from slither import Slither
from naga.naga import Naga

def test_one():
    set_solc('0.5.0')
    sol_file = '/data/disk_16t_2/kailun/smart_contract_centralization/test_contracts/etherscan_token/token20/contracts/0.5.0/0x0c6f5f7d555e7518f6841a79436bd2b1eef03381/CocosToken.sol'
    print(sol_file)
    slither = Slither(sol_file)
    naga = Naga(slither,'CocosToken','0x312ca0592a39a5fa5c87bb4f1da7b77544a91b87','erc20','0.5.0')

    for c in naga.entry_contracts:
        c.detect()
        for svar in c.label_svars_dict['owners']:
            print(svar)

        print(c.summary_json())

if __name__ == "__main__":
    test_one()