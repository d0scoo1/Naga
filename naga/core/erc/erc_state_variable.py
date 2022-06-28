#  state variable name, return function signature, type, possible names (lower names)
ERC20_STATE_VARIAVLES = [
    ('name','name()', 'string', ['name']),
    ('symbol','symbol()', 'string', ['symbol']),
    ('decimals','decimals()', 'uint', ['decimals']),
    ('totalSupply','totalSupply()', 'uint', ['totalsupply']),
    ('balances','balanceOf(address)', 'mapping(address => uint256)', ['balance']),
    ('allowances','allowance(address,address)','mapping(address => mapping(address => uint256))',['allow']),
]

ERC721_STATE_VARIAVLES = [
    ('name','name()', 'string', ['name']),
    ('symbol','symbol()', 'string', ['symbol']),
    ('ownerOf','ownerOf(uint256)','mapping(uint256 => address)',[],), # 这个owner不是管理员 owner
    ('balances','balanceOf(address)','mapping(address => uint256)',['balance']),
    ('tokenApprovals','getApproved(uint256)','mapping(address => uint256)',['tokenapproval']),
    ('operatorApprovals','isApprovedForAll(address, address)','mapping(address => mapping(address => bool))',['operatorapproval']),
    ('uri','tokenURI(uint256)','string',['uri'])
]
ERC1155_STATE_VARIAVLES = [
     ('balances','balanceOf(address, uint256)','mapping(uint256 => mapping(address => uint256))',['balance']),
    ('operatorApprovals','isApprovedForAll(address, address)','mapping(address => mapping(address => bool))',['operatorapproval']),
    ('uri','uri(uint256)','string',['uri']),
    ('totalSupply','totalSupply()', 'mapping(uint256 => uint256)', ['totalsupply'])
]