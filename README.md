# NAGA
A tool that detect overpowered owner in smart contracts.
# Preparation
## Python
Version: [3.8.10](https://www.python.org/downloads/release/python-3810/)

## Install solc-select
We use [solc-select](https://github.com/crytic/solc-select) to manage and switch [solc](https://github.com/ethereum/solidity) compilers.

`pip3 install solc-select`

Install solc all version

`solc-select install all`

If you cannot use the command `solc-select`, see [here](#set-path).


## Install Slither
[Slither](https://github.com/crytic/slither) is a Solidity static analysis framework written in Python 3.
Naga does contract analysis based on Slither.

`pip3 install slither-analyzer`

# Usages

    slither = Slither(sol_file)
    naga = Naga(slither)
    for c in naga.entry_contracts: # get the entry contracts
        if c.is_erc: # Naga supposes ERC-20 ERC-721 ERC-777
            c.detect()
            print(c.summary())
            #print(c.summary_json()) # Naga json report
            #print(c.summary_csv()) # Naga csv report


# Appendix

## Set PATH
Please make sure
`/home/your_username/.local/bin`
is in $PATH

You can check and update $PATH using the following commands

`echo $PATH`

`sudo vim /etc/profile`

`export PATH="/home/your_username/.local/bin:$PATH"`

`source /etc/profile`