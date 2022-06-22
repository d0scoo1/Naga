
from test_base import *
import logging
#logging.basicConfig(level=logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger()

def test_owners():

    set_solc('0.4.17')
    slither = Slither("tests/contracts/token_20_0xdAC17F958D2ee523a2206206994597C13D831ec7.sol")
    for c in slither.contracts_derived:
        print()
        c = ContractExp(c)
        print('contract:', c.contract.name)
        c.print()


if __name__ == "__main__":
    test_owners()
   