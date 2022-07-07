## Etherscan platform bugs fix
[Slither](https://github.com/crytic/slither) uses [crytic_compile](https://github.com/crytic/crytic-compile) to compile a contract.
The crytic_compile supports a lot of platforms ([list](https://github.com/crytic/crytic-compile/blob/master/crytic_compile/platform/all_platforms.py)), we use [Etherscan platform](https://github.com/crytic/crytic-compile/blob/master/crytic_compile/platform/etherscan.py) to download and compile contracts.
However, the Etherscan platform provided by crytic_compile has some bug, sometimes, it cannot `mkdirs` correctly.
We fix this bug in [etherscan.py](etherscan.py).

## Contract Project Support
Meanwhile, crytic_compile did not providing a platform that can support a controct project, specifically, we need to specify the main solidity file manually. We add a new platform (see [multiple_sol_files.py](multiple_sol_files.py)) that can automatically import all contracts in a folder.
