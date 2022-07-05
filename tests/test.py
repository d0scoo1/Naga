import sys
sys.path.append(r"/data/disk_16t_2/kailun/smart_contract_centralization/naga")

from solc_utils import set_solc
from slither import Slither
from naga.naga import Naga

def test_one():
    set_solc('0.8.0')
    sol_file = '/data/disk_16t_2/kailun/smart_contract_centralization/naga/tests/contracts/HelloERC20.sol'
    print(sol_file)

    slither = Slither(sol_file)

    naga = Naga(slither,None,'0x312ca0592a39a5fa5c87bb4f1da7b77544a91b87',None,'0.5.0')

    for c in naga.entry_contracts:
        c.detect()
        for svar in c.label_svars_dict['owners']:
            print(svar)

        print(c.summary_json())




if __name__ == "__main__":
    test_one()