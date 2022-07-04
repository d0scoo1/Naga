## Dataset

There are two datasets, [Etherscan Token Tracker](https://etherscan.io/tokens) and [smart contract sanctuary](https://github.com/tintinweb/smart-contract-sanctuary).

### Etherscan Token Tracker
We scraped [ERC20](https://etherscan.io/tokens) [ERC721](https://etherscan.io/tokens-nft) and [ERC1155](https://etherscan.io/tokens-nft1155) contracts on Etherscan. [July 1, 2022]

- ERC 20, total 930 contracts.
- ERC 721, because many of the lower ranked contracts do not have transactions, we only selected the top 10,000 contracts.
- ERC 1155, top 5000 contracts.

### Smart Contract Sanctuary
Smart Contract Sanctuary is a repository for ethereum smart contracts verified on Etherscan.

We select the Ethereum mainnet contracts as our test samples.
Yon can get those contracts [here](https://github.com/d0scoo1/smart-contract-sanctuary-ethereum/tree/master/contracts/mainnet).

## Tools
We provide two tools to process the above data, which you can find [here](smart_contract_centralization/naga/tools).