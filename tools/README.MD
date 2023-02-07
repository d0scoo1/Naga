
## Contract Sanctuary Util

[Smart contract sanctuary ethereum](https://github.com/tintinweb/smart-contract-sanctuary-ethereum) offers the contract of ETH.
The directory structure is *contracts/mainnet/index_of_contract_address/solidity_file*. We can get more information about a contract in the *contracts.json*.

To avoid selecting the compiler version each time, we use Contract Sacnctuary Util to pre-classify these contracts by version.

## ERC Standard

`token_generator.py` is a tool to get function signatures and state variables in the ERC.

## Ethersacn Spider

Etherscan Spider is a tool to spider contract lists in the Ethersacn.

We use this tool to get the [ERC-20](https://etherscan.io/tokens), [ERC-721](https://etherscan.io/tokens-nft) and [ERC-1155](https://etherscan.io/tokens-nft1155) contracts of Ethercan token tracker pages.

Then, we request contracts through Etherscan API (you can apply [here](https://etherscan.io/myapikey)).

This tool provides other functions, such as result parsing, compile testing, etc.

You should assign directories in the `token_info.py`