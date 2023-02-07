from collections import namedtuple
ERC_FUNCTION = namedtuple("ERC_FUNCTION", ["full_name", "name", "parameters", "return_type","visibility", "view", "events"])
ERC_EVENT = namedtuple("ERC_EVENT", ["full_name","name", "parameters", "indexes"])

"""
在 token 检查中，主要使用 IERC 中的函数签名来校验，由于都实现了接口，所以我们直接查找 IERC20/721/777/1155
"""

IERC20_FUNCTIONS = [
    ERC_FUNCTION("totalSupply()","totalSupply","[]","['uint256']","external","True","[]"),
    ERC_FUNCTION("balanceOf(address)","balanceOf","['address']","['uint256']","external","True","[]"),
    ERC_FUNCTION("transfer(address,uint256)","transfer","['address', 'uint256']","['bool']","external","False","[]"),
    ERC_FUNCTION("allowance(address,address)","allowance","['address', 'address']","['uint256']","external","True","[]"),
    ERC_FUNCTION("approve(address,uint256)","approve","['address', 'uint256']","['bool']","external","False","[]"),
    ERC_FUNCTION("transferFrom(address,address,uint256)","transferFrom","['address', 'address', 'uint256']","['bool']","external","False","[]"),
]
IERC20_EVENTS = [
    ERC_EVENT("Transfer(address,address,uint256)","Transfer","['address', 'address', 'uint256']","None"),
    ERC_EVENT("Approval(address,address,uint256)","Approval","['address', 'address', 'uint256']","None"),
]
ERC20_FUNCTIONS = [
    ERC_FUNCTION("constructor(string,string)","constructor","['string', 'string']","[]","public","False","[]"),
    ERC_FUNCTION("name()","name","[]","['string']","public","True","[]"),
    ERC_FUNCTION("symbol()","symbol","[]","['string']","public","True","[]"),
    ERC_FUNCTION("decimals()","decimals","[]","['uint8']","public","True","[]"),
    ERC_FUNCTION("totalSupply()","totalSupply","[]","['uint256']","public","True","[]"),
    ERC_FUNCTION("balanceOf(address)","balanceOf","['address']","['uint256']","public","True","[]"),
    ERC_FUNCTION("transfer(address,uint256)","transfer","['address', 'uint256']","['bool']","public","False","['Transfer(address,address,uint256)']"),
    ERC_FUNCTION("allowance(address,address)","allowance","['address', 'address']","['uint256']","public","True","[]"),
    ERC_FUNCTION("approve(address,uint256)","approve","['address', 'uint256']","['bool']","public","False","['Approval(address,address,uint256)']"),
    ERC_FUNCTION("transferFrom(address,address,uint256)","transferFrom","['address', 'address', 'uint256']","['bool']","public","False","['Transfer(address,address,uint256)', 'Approval(address,address,uint256)']"),
    ERC_FUNCTION("increaseAllowance(address,uint256)","increaseAllowance","['address', 'uint256']","['bool']","public","False","['Approval(address,address,uint256)']"),
    ERC_FUNCTION("decreaseAllowance(address,uint256)","decreaseAllowance","['address', 'uint256']","['bool']","public","False","['Approval(address,address,uint256)']"),
    ERC_FUNCTION("_transfer(address,address,uint256)","_transfer","['address', 'address', 'uint256']","[]","internal","False","['Transfer(address,address,uint256)']"),
    ERC_FUNCTION("_mint(address,uint256)","_mint","['address', 'uint256']","[]","internal","False","['Transfer(address,address,uint256)']"),
    ERC_FUNCTION("_burn(address,uint256)","_burn","['address', 'uint256']","[]","internal","False","['Transfer(address,address,uint256)']"),
    ERC_FUNCTION("_approve(address,address,uint256)","_approve","['address', 'address', 'uint256']","[]","internal","False","['Approval(address,address,uint256)']"),
    ERC_FUNCTION("_spendAllowance(address,address,uint256)","_spendAllowance","['address', 'address', 'uint256']","[]","internal","False","['Approval(address,address,uint256)']"),
    ERC_FUNCTION("_beforeTokenTransfer(address,address,uint256)","_beforeTokenTransfer","['address', 'address', 'uint256']","[]","internal","False","[]"),
    ERC_FUNCTION("_afterTokenTransfer(address,address,uint256)","_afterTokenTransfer","['address', 'address', 'uint256']","[]","internal","False","[]"),
]
ERC20_EVENTS = [
    ERC_EVENT("Transfer(address,address,uint256)","Transfer","['address', 'address', 'uint256']","None"),
    ERC_EVENT("Approval(address,address,uint256)","Approval","['address', 'address', 'uint256']","None"),
]
IERC20_FUNCTIONS_SIG = [
"totalSupply()","balanceOf(address)","transfer(address,uint256)","allowance(address,address)","approve(address,uint256)","transferFrom(address,address,uint256)",]
IERC20_EVENTS_SIG = [
"Transfer(address,address,uint256)","Approval(address,address,uint256)",]
ERC20_FUNCTIONS_SIG = [
"constructor(string,string)","name()","symbol()","decimals()","totalSupply()","balanceOf(address)","transfer(address,uint256)","allowance(address,address)","approve(address,uint256)","transferFrom(address,address,uint256)","increaseAllowance(address,uint256)","decreaseAllowance(address,uint256)","_transfer(address,address,uint256)","_mint(address,uint256)","_burn(address,uint256)","_approve(address,address,uint256)","_spendAllowance(address,address,uint256)","_beforeTokenTransfer(address,address,uint256)","_afterTokenTransfer(address,address,uint256)",]
ERC20_EVENTS_SIG = [
"Transfer(address,address,uint256)","Approval(address,address,uint256)",]

IERC721_FUNCTIONS = [
    ERC_FUNCTION("balanceOf(address)","balanceOf","['address']","['uint256']","external","True","[]"),
    ERC_FUNCTION("ownerOf(uint256)","ownerOf","['uint256']","['address']","external","True","[]"),
    ERC_FUNCTION("safeTransferFrom(address,address,uint256)","safeTransferFrom","['address', 'address', 'uint256']","[]","external","False","[]"),
    ERC_FUNCTION("transferFrom(address,address,uint256)","transferFrom","['address', 'address', 'uint256']","[]","external","False","[]"),
    ERC_FUNCTION("approve(address,uint256)","approve","['address', 'uint256']","[]","external","False","[]"),
    ERC_FUNCTION("getApproved(uint256)","getApproved","['uint256']","['address']","external","True","[]"),
    ERC_FUNCTION("setApprovalForAll(address,bool)","setApprovalForAll","['address', 'bool']","[]","external","False","[]"),
    ERC_FUNCTION("isApprovedForAll(address,address)","isApprovedForAll","['address', 'address']","['bool']","external","True","[]"),
    ERC_FUNCTION("safeTransferFrom(address,address,uint256,bytes)","safeTransferFrom","['address', 'address', 'uint256', 'bytes']","[]","external","False","[]"),
]
IERC721_EVENTS = [
    ERC_EVENT("Transfer(address,address,uint256)","Transfer","['address', 'address', 'uint256']","None"),
    ERC_EVENT("Approval(address,address,uint256)","Approval","['address', 'address', 'uint256']","None"),
    ERC_EVENT("ApprovalForAll(address,address,bool)","ApprovalForAll","['address', 'address', 'bool']","None"),
]
ERC721_FUNCTIONS = [
    ERC_FUNCTION("constructor(string,string)","constructor","['string', 'string']","[]","public","False","[]"),
    ERC_FUNCTION("supportsInterface(bytes4)","supportsInterface","['bytes4']","['bool']","public","True","[]"),
    ERC_FUNCTION("balanceOf(address)","balanceOf","['address']","['uint256']","public","True","[]"),
    ERC_FUNCTION("ownerOf(uint256)","ownerOf","['uint256']","['address']","public","True","[]"),
    ERC_FUNCTION("name()","name","[]","['string']","public","True","[]"),
    ERC_FUNCTION("symbol()","symbol","[]","['string']","public","True","[]"),
    ERC_FUNCTION("tokenURI(uint256)","tokenURI","['uint256']","['string']","public","True","[]"),
    ERC_FUNCTION("_baseURI()","_baseURI","[]","['string']","internal","True","[]"),
    ERC_FUNCTION("approve(address,uint256)","approve","['address', 'uint256']","[]","public","False","['Approval(address,address,uint256)']"),
    ERC_FUNCTION("getApproved(uint256)","getApproved","['uint256']","['address']","public","True","[]"),
    ERC_FUNCTION("setApprovalForAll(address,bool)","setApprovalForAll","['address', 'bool']","[]","public","False","['ApprovalForAll(address,address,bool)']"),
    ERC_FUNCTION("isApprovedForAll(address,address)","isApprovedForAll","['address', 'address']","['bool']","public","True","[]"),
    ERC_FUNCTION("transferFrom(address,address,uint256)","transferFrom","['address', 'address', 'uint256']","[]","public","False","['Transfer(address,address,uint256)', 'Approval(address,address,uint256)']"),
    ERC_FUNCTION("safeTransferFrom(address,address,uint256)","safeTransferFrom","['address', 'address', 'uint256']","[]","public","False","['Transfer(address,address,uint256)', 'Approval(address,address,uint256)']"),
    ERC_FUNCTION("safeTransferFrom(address,address,uint256,bytes)","safeTransferFrom","['address', 'address', 'uint256', 'bytes']","[]","public","False","['Transfer(address,address,uint256)', 'Approval(address,address,uint256)']"),
    ERC_FUNCTION("_safeTransfer(address,address,uint256,bytes)","_safeTransfer","['address', 'address', 'uint256', 'bytes']","[]","internal","False","['Transfer(address,address,uint256)', 'Approval(address,address,uint256)']"),
    ERC_FUNCTION("_exists(uint256)","_exists","['uint256']","['bool']","internal","True","[]"),
    ERC_FUNCTION("_isApprovedOrOwner(address,uint256)","_isApprovedOrOwner","['address', 'uint256']","['bool']","internal","True","[]"),
    ERC_FUNCTION("_safeMint(address,uint256)","_safeMint","['address', 'uint256']","[]","internal","False","['Transfer(address,address,uint256)']"),
    ERC_FUNCTION("_safeMint(address,uint256,bytes)","_safeMint","['address', 'uint256', 'bytes']","[]","internal","False","['Transfer(address,address,uint256)']"),
    ERC_FUNCTION("_mint(address,uint256)","_mint","['address', 'uint256']","[]","internal","False","['Transfer(address,address,uint256)']"),
    ERC_FUNCTION("_burn(uint256)","_burn","['uint256']","[]","internal","False","['Approval(address,address,uint256)', 'Transfer(address,address,uint256)']"),
    ERC_FUNCTION("_transfer(address,address,uint256)","_transfer","['address', 'address', 'uint256']","[]","internal","False","['Transfer(address,address,uint256)', 'Approval(address,address,uint256)']"),
    ERC_FUNCTION("_approve(address,uint256)","_approve","['address', 'uint256']","[]","internal","False","['Approval(address,address,uint256)']"),
    ERC_FUNCTION("_setApprovalForAll(address,address,bool)","_setApprovalForAll","['address', 'address', 'bool']","[]","internal","False","['ApprovalForAll(address,address,bool)']"),
    ERC_FUNCTION("_checkOnERC721Received(address,address,uint256,bytes)","_checkOnERC721Received","['address', 'address', 'uint256', 'bytes']","['bool']","private","False","[]"),
    ERC_FUNCTION("_beforeTokenTransfer(address,address,uint256)","_beforeTokenTransfer","['address', 'address', 'uint256']","[]","internal","False","[]"),
    ERC_FUNCTION("_afterTokenTransfer(address,address,uint256)","_afterTokenTransfer","['address', 'address', 'uint256']","[]","internal","False","[]"),
]
ERC721_EVENTS = [
    ERC_EVENT("Transfer(address,address,uint256)","Transfer","['address', 'address', 'uint256']","None"),
    ERC_EVENT("Approval(address,address,uint256)","Approval","['address', 'address', 'uint256']","None"),
    ERC_EVENT("ApprovalForAll(address,address,bool)","ApprovalForAll","['address', 'address', 'bool']","None"),
]
IERC721_FUNCTIONS_SIG = [
"balanceOf(address)","ownerOf(uint256)","safeTransferFrom(address,address,uint256)","transferFrom(address,address,uint256)","approve(address,uint256)","getApproved(uint256)","setApprovalForAll(address,bool)","isApprovedForAll(address,address)","safeTransferFrom(address,address,uint256,bytes)",]
IERC721_EVENTS_SIG = [
"Transfer(address,address,uint256)","Approval(address,address,uint256)","ApprovalForAll(address,address,bool)",]
ERC721_FUNCTIONS_SIG = [
"constructor(string,string)","supportsInterface(bytes4)","balanceOf(address)","ownerOf(uint256)","name()","symbol()","tokenURI(uint256)","_baseURI()","approve(address,uint256)","getApproved(uint256)","setApprovalForAll(address,bool)","isApprovedForAll(address,address)","transferFrom(address,address,uint256)","safeTransferFrom(address,address,uint256)","safeTransferFrom(address,address,uint256,bytes)","_safeTransfer(address,address,uint256,bytes)","_exists(uint256)","_isApprovedOrOwner(address,uint256)","_safeMint(address,uint256)","_safeMint(address,uint256,bytes)","_mint(address,uint256)","_burn(uint256)","_transfer(address,address,uint256)","_approve(address,uint256)","_setApprovalForAll(address,address,bool)","_checkOnERC721Received(address,address,uint256,bytes)","_beforeTokenTransfer(address,address,uint256)","_afterTokenTransfer(address,address,uint256)",]
ERC721_EVENTS_SIG = [
"Transfer(address,address,uint256)","Approval(address,address,uint256)","ApprovalForAll(address,address,bool)",]

IERC777_FUNCTIONS = [
    ERC_FUNCTION("name()","name","[]","['string']","external","True","[]"),
    ERC_FUNCTION("symbol()","symbol","[]","['string']","external","True","[]"),
    ERC_FUNCTION("granularity()","granularity","[]","['uint256']","external","True","[]"),
    ERC_FUNCTION("totalSupply()","totalSupply","[]","['uint256']","external","True","[]"),
    ERC_FUNCTION("balanceOf(address)","balanceOf","['address']","['uint256']","external","True","[]"),
    ERC_FUNCTION("send(address,uint256,bytes)","send","['address', 'uint256', 'bytes']","[]","external","False","[]"),
    ERC_FUNCTION("burn(uint256,bytes)","burn","['uint256', 'bytes']","[]","external","False","[]"),
    ERC_FUNCTION("isOperatorFor(address,address)","isOperatorFor","['address', 'address']","['bool']","external","True","[]"),
    ERC_FUNCTION("authorizeOperator(address)","authorizeOperator","['address']","[]","external","False","[]"),
    ERC_FUNCTION("revokeOperator(address)","revokeOperator","['address']","[]","external","False","[]"),
    ERC_FUNCTION("defaultOperators()","defaultOperators","[]","['address[]']","external","True","[]"),
    ERC_FUNCTION("operatorSend(address,address,uint256,bytes,bytes)","operatorSend","['address', 'address', 'uint256', 'bytes', 'bytes']","[]","external","False","[]"),
    ERC_FUNCTION("operatorBurn(address,uint256,bytes,bytes)","operatorBurn","['address', 'uint256', 'bytes', 'bytes']","[]","external","False","[]"),
]
IERC777_EVENTS = [
    ERC_EVENT("Sent(address,address,address,uint256,bytes,bytes)","Sent","['address', 'address', 'address', 'uint256', 'bytes', 'bytes']","None"),
    ERC_EVENT("Minted(address,address,uint256,bytes,bytes)","Minted","['address', 'address', 'uint256', 'bytes', 'bytes']","None"),
    ERC_EVENT("Burned(address,address,uint256,bytes,bytes)","Burned","['address', 'address', 'uint256', 'bytes', 'bytes']","None"),
    ERC_EVENT("AuthorizedOperator(address,address)","AuthorizedOperator","['address', 'address']","None"),
    ERC_EVENT("RevokedOperator(address,address)","RevokedOperator","['address', 'address']","None"),
]
ERC777_FUNCTIONS = [
    ERC_FUNCTION("constructor(string,string,address[])","constructor","['string', 'string', 'address[]']","[]","public","False","[]"),
    ERC_FUNCTION("name()","name","[]","['string']","public","True","[]"),
    ERC_FUNCTION("symbol()","symbol","[]","['string']","public","True","[]"),
    ERC_FUNCTION("decimals()","decimals","[]","['uint8']","public","True","[]"),
    ERC_FUNCTION("granularity()","granularity","[]","['uint256']","public","True","[]"),
    ERC_FUNCTION("totalSupply()","totalSupply","[]","['uint256']","public","True","[]"),
    ERC_FUNCTION("balanceOf(address)","balanceOf","['address']","['uint256']","public","True","[]"),
    ERC_FUNCTION("send(address,uint256,bytes)","send","['address', 'uint256', 'bytes']","[]","public","False","['Transfer(address,address,uint256)', 'Sent(address,address,address,uint256,bytes,bytes)']"),
    ERC_FUNCTION("transfer(address,uint256)","transfer","['address', 'uint256']","['bool']","public","False","['Transfer(address,address,uint256)', 'Sent(address,address,address,uint256,bytes,bytes)']"),
    ERC_FUNCTION("burn(uint256,bytes)","burn","['uint256', 'bytes']","[]","public","False","['Burned(address,address,uint256,bytes,bytes)', 'Transfer(address,address,uint256)']"),
    ERC_FUNCTION("isOperatorFor(address,address)","isOperatorFor","['address', 'address']","['bool']","public","True","[]"),
    ERC_FUNCTION("authorizeOperator(address)","authorizeOperator","['address']","[]","public","False","['AuthorizedOperator(address,address)']"),
    ERC_FUNCTION("revokeOperator(address)","revokeOperator","['address']","[]","public","False","['RevokedOperator(address,address)']"),
    ERC_FUNCTION("defaultOperators()","defaultOperators","[]","['address[]']","public","True","[]"),
    ERC_FUNCTION("operatorSend(address,address,uint256,bytes,bytes)","operatorSend","['address', 'address', 'uint256', 'bytes', 'bytes']","[]","public","False","['Transfer(address,address,uint256)', 'Sent(address,address,address,uint256,bytes,bytes)']"),
    ERC_FUNCTION("operatorBurn(address,uint256,bytes,bytes)","operatorBurn","['address', 'uint256', 'bytes', 'bytes']","[]","public","False","['Burned(address,address,uint256,bytes,bytes)', 'Transfer(address,address,uint256)']"),
    ERC_FUNCTION("allowance(address,address)","allowance","['address', 'address']","['uint256']","public","True","[]"),
    ERC_FUNCTION("approve(address,uint256)","approve","['address', 'uint256']","['bool']","public","False","['Approval(address,address,uint256)']"),
    ERC_FUNCTION("transferFrom(address,address,uint256)","transferFrom","['address', 'address', 'uint256']","['bool']","public","False","['Transfer(address,address,uint256)', 'Sent(address,address,address,uint256,bytes,bytes)', 'Approval(address,address,uint256)']"),
    ERC_FUNCTION("_mint(address,uint256,bytes,bytes)","_mint","['address', 'uint256', 'bytes', 'bytes']","[]","internal","False","['Minted(address,address,uint256,bytes,bytes)', 'Transfer(address,address,uint256)']"),
    ERC_FUNCTION("_mint(address,uint256,bytes,bytes,bool)","_mint","['address', 'uint256', 'bytes', 'bytes', 'bool']","[]","internal","False","['Minted(address,address,uint256,bytes,bytes)', 'Transfer(address,address,uint256)']"),
    ERC_FUNCTION("_send(address,address,uint256,bytes,bytes,bool)","_send","['address', 'address', 'uint256', 'bytes', 'bytes', 'bool']","[]","internal","False","['Transfer(address,address,uint256)', 'Sent(address,address,address,uint256,bytes,bytes)']"),
    ERC_FUNCTION("_burn(address,uint256,bytes,bytes)","_burn","['address', 'uint256', 'bytes', 'bytes']","[]","internal","False","['Burned(address,address,uint256,bytes,bytes)', 'Transfer(address,address,uint256)']"),
    ERC_FUNCTION("_move(address,address,address,uint256,bytes,bytes)","_move","['address', 'address', 'address', 'uint256', 'bytes', 'bytes']","[]","private","False","['Transfer(address,address,uint256)', 'Sent(address,address,address,uint256,bytes,bytes)']"),
    ERC_FUNCTION("_approve(address,address,uint256)","_approve","['address', 'address', 'uint256']","[]","internal","False","['Approval(address,address,uint256)']"),
    ERC_FUNCTION("_callTokensToSend(address,address,address,uint256,bytes,bytes)","_callTokensToSend","['address', 'address', 'address', 'uint256', 'bytes', 'bytes']","[]","private","False","[]"),
    ERC_FUNCTION("_callTokensReceived(address,address,address,uint256,bytes,bytes,bool)","_callTokensReceived","['address', 'address', 'address', 'uint256', 'bytes', 'bytes', 'bool']","[]","private","False","[]"),
    ERC_FUNCTION("_spendAllowance(address,address,uint256)","_spendAllowance","['address', 'address', 'uint256']","[]","internal","False","['Approval(address,address,uint256)']"),
    ERC_FUNCTION("_beforeTokenTransfer(address,address,address,uint256)","_beforeTokenTransfer","['address', 'address', 'address', 'uint256']","[]","internal","False","[]"),
    ERC_FUNCTION("slitherConstructorConstantVariables()","slitherConstructorConstantVariables","[]","[]","internal","False","[]"),
]
ERC777_EVENTS = [
    ERC_EVENT("Sent(address,address,address,uint256,bytes,bytes)","Sent","['address', 'address', 'address', 'uint256', 'bytes', 'bytes']","None"),
    ERC_EVENT("Minted(address,address,uint256,bytes,bytes)","Minted","['address', 'address', 'uint256', 'bytes', 'bytes']","None"),
    ERC_EVENT("Burned(address,address,uint256,bytes,bytes)","Burned","['address', 'address', 'uint256', 'bytes', 'bytes']","None"),
    ERC_EVENT("AuthorizedOperator(address,address)","AuthorizedOperator","['address', 'address']","None"),
    ERC_EVENT("RevokedOperator(address,address)","RevokedOperator","['address', 'address']","None"),
    ERC_EVENT("Transfer(address,address,uint256)","Transfer","['address', 'address', 'uint256']","None"),
    ERC_EVENT("Approval(address,address,uint256)","Approval","['address', 'address', 'uint256']","None"),
]
IERC777_FUNCTIONS_SIG = [
"name()","symbol()","granularity()","totalSupply()","balanceOf(address)","send(address,uint256,bytes)","burn(uint256,bytes)","isOperatorFor(address,address)","authorizeOperator(address)","revokeOperator(address)","defaultOperators()","operatorSend(address,address,uint256,bytes,bytes)","operatorBurn(address,uint256,bytes,bytes)",]
IERC777_EVENTS_SIG = [
"Sent(address,address,address,uint256,bytes,bytes)","Minted(address,address,uint256,bytes,bytes)","Burned(address,address,uint256,bytes,bytes)","AuthorizedOperator(address,address)","RevokedOperator(address,address)",]
ERC777_FUNCTIONS_SIG = [
"constructor(string,string,address[])","name()","symbol()","decimals()","granularity()","totalSupply()","balanceOf(address)","send(address,uint256,bytes)","transfer(address,uint256)","burn(uint256,bytes)","isOperatorFor(address,address)","authorizeOperator(address)","revokeOperator(address)","defaultOperators()","operatorSend(address,address,uint256,bytes,bytes)","operatorBurn(address,uint256,bytes,bytes)","allowance(address,address)","approve(address,uint256)","transferFrom(address,address,uint256)","_mint(address,uint256,bytes,bytes)","_mint(address,uint256,bytes,bytes,bool)","_send(address,address,uint256,bytes,bytes,bool)","_burn(address,uint256,bytes,bytes)","_move(address,address,address,uint256,bytes,bytes)","_approve(address,address,uint256)","_callTokensToSend(address,address,address,uint256,bytes,bytes)","_callTokensReceived(address,address,address,uint256,bytes,bytes,bool)","_spendAllowance(address,address,uint256)","_beforeTokenTransfer(address,address,address,uint256)","slitherConstructorConstantVariables()",]
ERC777_EVENTS_SIG = [
"Sent(address,address,address,uint256,bytes,bytes)","Minted(address,address,uint256,bytes,bytes)","Burned(address,address,uint256,bytes,bytes)","AuthorizedOperator(address,address)","RevokedOperator(address,address)","Transfer(address,address,uint256)","Approval(address,address,uint256)",]

IERC1155_FUNCTIONS = [
    ERC_FUNCTION("balanceOf(address,uint256)","balanceOf","['address', 'uint256']","['uint256']","external","True","[]"),
    ERC_FUNCTION("balanceOfBatch(address[],uint256[])","balanceOfBatch","['address[]', 'uint256[]']","['uint256[]']","external","True","[]"),
    ERC_FUNCTION("setApprovalForAll(address,bool)","setApprovalForAll","['address', 'bool']","[]","external","False","[]"),
    ERC_FUNCTION("isApprovedForAll(address,address)","isApprovedForAll","['address', 'address']","['bool']","external","True","[]"),
    ERC_FUNCTION("safeTransferFrom(address,address,uint256,uint256,bytes)","safeTransferFrom","['address', 'address', 'uint256', 'uint256', 'bytes']","[]","external","False","[]"),
    ERC_FUNCTION("safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)","safeBatchTransferFrom","['address', 'address', 'uint256[]', 'uint256[]', 'bytes']","[]","external","False","[]"),
]
IERC1155_EVENTS = [
    ERC_EVENT("TransferSingle(address,address,address,uint256,uint256)","TransferSingle","['address', 'address', 'address', 'uint256', 'uint256']","None"),
    ERC_EVENT("TransferBatch(address,address,address,uint256[],uint256[])","TransferBatch","['address', 'address', 'address', 'uint256[]', 'uint256[]']","None"),
    ERC_EVENT("ApprovalForAll(address,address,bool)","ApprovalForAll","['address', 'address', 'bool']","None"),
    ERC_EVENT("URI(string,uint256)","URI","['string', 'uint256']","None"),
]
ERC1155_FUNCTIONS = [
    ERC_FUNCTION("constructor(string)","constructor","['string']","[]","public","False","[]"),
    ERC_FUNCTION("supportsInterface(bytes4)","supportsInterface","['bytes4']","['bool']","public","True","[]"),
    ERC_FUNCTION("uri(uint256)","uri","['uint256']","['string']","public","True","[]"),
    ERC_FUNCTION("balanceOf(address,uint256)","balanceOf","['address', 'uint256']","['uint256']","public","True","[]"),
    ERC_FUNCTION("balanceOfBatch(address[],uint256[])","balanceOfBatch","['address[]', 'uint256[]']","['uint256[]']","public","True","[]"),
    ERC_FUNCTION("setApprovalForAll(address,bool)","setApprovalForAll","['address', 'bool']","[]","public","False","['ApprovalForAll(address,address,bool)']"),
    ERC_FUNCTION("isApprovedForAll(address,address)","isApprovedForAll","['address', 'address']","['bool']","public","True","[]"),
    ERC_FUNCTION("safeTransferFrom(address,address,uint256,uint256,bytes)","safeTransferFrom","['address', 'address', 'uint256', 'uint256', 'bytes']","[]","public","False","['TransferSingle(address,address,address,uint256,uint256)']"),
    ERC_FUNCTION("safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)","safeBatchTransferFrom","['address', 'address', 'uint256[]', 'uint256[]', 'bytes']","[]","public","False","['TransferBatch(address,address,address,uint256[],uint256[])']"),
    ERC_FUNCTION("_safeTransferFrom(address,address,uint256,uint256,bytes)","_safeTransferFrom","['address', 'address', 'uint256', 'uint256', 'bytes']","[]","internal","False","['TransferSingle(address,address,address,uint256,uint256)']"),
    ERC_FUNCTION("_safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)","_safeBatchTransferFrom","['address', 'address', 'uint256[]', 'uint256[]', 'bytes']","[]","internal","False","['TransferBatch(address,address,address,uint256[],uint256[])']"),
    ERC_FUNCTION("_setURI(string)","_setURI","['string']","[]","internal","False","[]"),
    ERC_FUNCTION("_mint(address,uint256,uint256,bytes)","_mint","['address', 'uint256', 'uint256', 'bytes']","[]","internal","False","['TransferSingle(address,address,address,uint256,uint256)']"),
    ERC_FUNCTION("_mintBatch(address,uint256[],uint256[],bytes)","_mintBatch","['address', 'uint256[]', 'uint256[]', 'bytes']","[]","internal","False","['TransferBatch(address,address,address,uint256[],uint256[])']"),
    ERC_FUNCTION("_burn(address,uint256,uint256)","_burn","['address', 'uint256', 'uint256']","[]","internal","False","['TransferSingle(address,address,address,uint256,uint256)']"),
    ERC_FUNCTION("_burnBatch(address,uint256[],uint256[])","_burnBatch","['address', 'uint256[]', 'uint256[]']","[]","internal","False","['TransferBatch(address,address,address,uint256[],uint256[])']"),
    ERC_FUNCTION("_setApprovalForAll(address,address,bool)","_setApprovalForAll","['address', 'address', 'bool']","[]","internal","False","['ApprovalForAll(address,address,bool)']"),
    ERC_FUNCTION("_beforeTokenTransfer(address,address,address,uint256[],uint256[],bytes)","_beforeTokenTransfer","['address', 'address', 'address', 'uint256[]', 'uint256[]', 'bytes']","[]","internal","False","[]"),
    ERC_FUNCTION("_afterTokenTransfer(address,address,address,uint256[],uint256[],bytes)","_afterTokenTransfer","['address', 'address', 'address', 'uint256[]', 'uint256[]', 'bytes']","[]","internal","False","[]"),
    ERC_FUNCTION("_doSafeTransferAcceptanceCheck(address,address,address,uint256,uint256,bytes)","_doSafeTransferAcceptanceCheck","['address', 'address', 'address', 'uint256', 'uint256', 'bytes']","[]","private","False","[]"),
    ERC_FUNCTION("_doSafeBatchTransferAcceptanceCheck(address,address,address,uint256[],uint256[],bytes)","_doSafeBatchTransferAcceptanceCheck","['address', 'address', 'address', 'uint256[]', 'uint256[]', 'bytes']","[]","private","False","[]"),
    ERC_FUNCTION("_asSingletonArray(uint256)","_asSingletonArray","['uint256']","['uint256[]']","private","True","[]"),
]
ERC1155_EVENTS = [
    ERC_EVENT("TransferSingle(address,address,address,uint256,uint256)","TransferSingle","['address', 'address', 'address', 'uint256', 'uint256']","None"),
    ERC_EVENT("TransferBatch(address,address,address,uint256[],uint256[])","TransferBatch","['address', 'address', 'address', 'uint256[]', 'uint256[]']","None"),
    ERC_EVENT("ApprovalForAll(address,address,bool)","ApprovalForAll","['address', 'address', 'bool']","None"),
    ERC_EVENT("URI(string,uint256)","URI","['string', 'uint256']","None"),
]
IERC1155_FUNCTIONS_SIG = [
"balanceOf(address,uint256)","balanceOfBatch(address[],uint256[])","setApprovalForAll(address,bool)","isApprovedForAll(address,address)","safeTransferFrom(address,address,uint256,uint256,bytes)","safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)",]
IERC1155_EVENTS_SIG = [
"TransferSingle(address,address,address,uint256,uint256)","TransferBatch(address,address,address,uint256[],uint256[])","ApprovalForAll(address,address,bool)","URI(string,uint256)",]
ERC1155_FUNCTIONS_SIG = [
"constructor(string)","supportsInterface(bytes4)","uri(uint256)","balanceOf(address,uint256)","balanceOfBatch(address[],uint256[])","setApprovalForAll(address,bool)","isApprovedForAll(address,address)","safeTransferFrom(address,address,uint256,uint256,bytes)","safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)","_safeTransferFrom(address,address,uint256,uint256,bytes)","_safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)","_setURI(string)","_mint(address,uint256,uint256,bytes)","_mintBatch(address,uint256[],uint256[],bytes)","_burn(address,uint256,uint256)","_burnBatch(address,uint256[],uint256[])","_setApprovalForAll(address,address,bool)","_beforeTokenTransfer(address,address,address,uint256[],uint256[],bytes)","_afterTokenTransfer(address,address,address,uint256[],uint256[],bytes)","_doSafeTransferAcceptanceCheck(address,address,address,uint256,uint256,bytes)","_doSafeBatchTransferAcceptanceCheck(address,address,address,uint256[],uint256[],bytes)","_asSingletonArray(uint256)",]
ERC1155_EVENTS_SIG = [
"TransferSingle(address,address,address,uint256,uint256)","TransferBatch(address,address,address,uint256[],uint256[])","ApprovalForAll(address,address,bool)","URI(string,uint256)",]
