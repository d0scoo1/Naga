import sys
sys.path.append(r"/data/disk_16t_2/kailun/smart_contract_centralization/naga")

from solc_utils import set_solc
from slither import Slither
from naga.naga import Naga

def test_one():
    set_solc('0.8.7')
    sol_file = '/data/disk_16t_2/kailun/smart_contract_centralization/test_contracts/etherscan_token/token20/contracts/0.8.1/0xdef1fac7bf08f173d286bbbdcbeeade695129840/DefiFactoryToken.sol'
    print(sol_file)
    slither = None
    try:
        slither = Slither(sol_file)
    except:
        print('slither error')
        return

    naga = Naga(slither,'Items','0x312ca0592a39a5fa5c87bb4f1da7b77544a91b87',None,'0.5.0')

    for c in naga.entry_contracts:
        c.detect()
        for svar in c.label_svars_dict['owners']:
            print(svar)

        #print(c.summary_json())

if __name__ == "__main__":
    test_one()