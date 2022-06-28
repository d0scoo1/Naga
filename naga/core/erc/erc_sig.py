IERC20_FUNCTIONS_SIG = [
"totalSupply()","balanceOf(address)","transfer(address,uint256)","allowance(address,address)","approve(address,uint256)","transferFrom(address,address,uint256)",]
IERC20_EVENTS_SIG = [
"Transfer(address,address,uint256)","Approval(address,address,uint256)",]


IERC721_FUNCTIONS_SIG = [
"balanceOf(address)","ownerOf(uint256)","safeTransferFrom(address,address,uint256)","transferFrom(address,address,uint256)","approve(address,uint256)","getApproved(uint256)","setApprovalForAll(address,bool)","isApprovedForAll(address,address)","safeTransferFrom(address,address,uint256,bytes)",]
IERC721_EVENTS_SIG = [
"Transfer(address,address,uint256)","Approval(address,address,uint256)","ApprovalForAll(address,address,bool)",]

IERC777_FUNCTIONS_SIG = [
"name()","symbol()","granularity()","totalSupply()","balanceOf(address)","send(address,uint256,bytes)","burn(uint256,bytes)","isOperatorFor(address,address)","authorizeOperator(address)","revokeOperator(address)","defaultOperators()","operatorSend(address,address,uint256,bytes,bytes)","operatorBurn(address,uint256,bytes,bytes)",]
IERC777_EVENTS_SIG = [
"Sent(address,address,address,uint256,bytes,bytes)","Minted(address,address,uint256,bytes,bytes)","Burned(address,address,uint256,bytes,bytes)","AuthorizedOperator(address,address)","RevokedOperator(address,address)",]

IERC1155_FUNCTIONS_SIG = [
"balanceOf(address,uint256)","balanceOfBatch(address[],uint256[])","setApprovalForAll(address,bool)","isApprovedForAll(address,address)","safeTransferFrom(address,address,uint256,uint256,bytes)","safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)",]
IERC1155_EVENTS_SIG = [
"TransferSingle(address,address,address,uint256,uint256)","TransferBatch(address,address,address,uint256[],uint256[])","ApprovalForAll(address,address,bool)","URI(string,uint256)",]


ERC20_WRITE_FUNCS_SIG = ["transfer(address,uint256)","approve(address,uint256)","transferFrom(address,address,uint256)"]
ERC721_WRITE_FUNCS_SIG = ["safeTransferFrom(address,address,uint256)","transferFrom(address,address,uint256)","approve(address,uint256)","setApprovalForAll(address,bool)","safeTransferFrom(address,address,uint256,bytes)"]
ERC1155_WRITE_FUNCS_SIG = [
"setApprovalForAll(address,bool)","safeTransferFrom(address,address,uint256,uint256,bytes)","safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)",]