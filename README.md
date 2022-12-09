# NAGA
A tool that detect overpowered owner in smart contracts.


## Install
Naga requires Python 3.8.10, solc-select and Slither.

### Install Python
Version: [3.8.10](https://www.python.org/downloads/release/python-3810/)

### Install solc-select
We use [solc-select](https://github.com/crytic/solc-select) to manage and switch [solc](https://github.com/ethereum/solidity) compilers.

```bash
pip3 install solc-select
```
Install solc all versions
```bash
solc-select install all
```

If you cannot use the command `solc-select`, see [Set PATH](#set-path).

### Install Slither
[Slither](https://github.com/crytic/slither) is a Solidity static analysis framework written in Python3.
Naga does contract analysis based on Slither.
```bash
pip3 install slither-analyzer
```

## Usages
Naga loads a slither object to detect overpowered owner in contracts.

```python
sol_file = "your_contract.sol"
contract_name = None # You can specify the entry contract name, if None, Naga will automatically try to find the entry contract.
erc_force = None # erc20, erc721, erc777, None.

slither = Slither(sol_file)
naga = Naga(slither)
naga.detect_entry_contract(er_force=erc_force) # Detect the entry contract
entry_c = naga.entry_contract # Get the entry contract object
entry_c.output(output_file="output.json") # Output the result to output.json
summary = entry_c.output() # Or just get the summary
```

`naga/detectors/` defines the detectors.
You can register your own detectors by adding them to `naga/detectors/`.

```python
slither = Slither(sol_file)
naga = Naga(slither)
entry_c = naga.entry_contract
naga.detect(entry_c,erc_force=None,detectors=[]) # Specify the detectors you want to use
entry_c.output(output_file="output.json")
```


## Appendix
### Dataset
[Here](https://github.com/d0scoo1/naga_contracts) is a dataset with more than 10,000 contracts.

### Set PATH
Please make sure
`/home/your_username/.local/bin`
is in $PATH

You can check and update $PATH using the following commands

`echo $PATH`

`sudo vim /etc/profile`

`export PATH="/home/your_username/.local/bin:$PATH"`

`source /etc/profile`