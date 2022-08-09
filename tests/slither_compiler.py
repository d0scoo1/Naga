from slither import Slither
from crytic_compile import CryticCompile
#from crytic_compile.platform.all_platforms import Etherscan,Solc
from test_platform.multiple_sol_files import MultiSolFiles
from test_platform.etherscan import Etherscan # crytic_compile.platform.Etherscan has bug

import logging
logging.getLogger("CryticCompile").level = logging.CRITICAL
from func_timeout import func_set_timeout

###### common config ######
etherscan_api_key= '68I2GBGUU79X6YSIMA8KVGIMYSKTS6UDPI'
solc_dir = '/home/yankailun/naga_test/tools/solc/'
openzeppelin_dir = '/home/yankailun/naga_test/tools/openzeppelin-contracts'

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

time_out_seconds = 60

@func_set_timeout(time_out_seconds)
def single_compile(sol_path,compiler_version):
    return Slither(sol_path,
        solc = get_solc(compiler_version),
        disable_solc_warnings = True,
        solc_remaps = get_solc_remaps(compiler_version)
    )

@func_set_timeout(time_out_seconds)
def multi_compile(sol_dir,compiler_version):
    return Slither(CryticCompile
                    (MultiSolFiles(
                        sol_dir,solc_remaps = get_solc_remaps(compiler_version)),
                    solc = get_solc(compiler_version),
                    compiler_version=compiler_version),
                disable_solc_warnings = True)

@func_set_timeout(time_out_seconds)
def etherscan_download_compile(contract_address,compiler_version,contracts_dir):
    return Slither(
        CryticCompile(
            Etherscan(contract_address,disable_solc_warnings = True),
            solc = get_solc(compiler_version),
            solc_remaps = get_solc_remaps(compiler_version),etherscan_only_source_code = True,
            etherscan_api_key=etherscan_api_key,
            export_dir =contracts_dir))

def get_solc(compiler_version):
    return solc_dir +'solc-'+ compiler_version

from func_timeout.exceptions import FunctionTimedOut
if __name__ == "__main__":
    #/home/yankailun/naga_test/token_tracker/erc1155/contracts/0x6737771b9e3d64b482b76e274ba77a612b564863_ContributionBoard
    try:
        slither = multi_compile('/home/yankailun/naga_test/token_tracker/erc1155/contracts/0x6737771b9e3d64b482b76e274ba77a612b564863_ContributionBoard','0.7.6')
    except FunctionTimedOut:
        print('timeout')

    #slither = multi_compile('/home/yankailun/naga_test/mainnet/contracts/0x1273e2854f716c39f8657b9e41846e3acf253a76_MercedesBenz','0.8.7')
    #print(slither)
    #for c in slither.contracts:
    #    print(c.name)