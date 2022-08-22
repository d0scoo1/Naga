#  state variable name, return function signature, type, possible names (lower names)
ERC20_STATE_VARIAVLES = [
    ('name','name()', 'string', ['name']),
    ('symbol','symbol()', 'string', ['symbol']),
    ('decimals','decimals()', 'uint', ['decimals','decimal']),
    ('totalSupply','totalSupply()', 'uint', ['totalsupply','supply']),
    ('balances','balanceOf(address)', 'mapping(address => uint256)', ['balances','balance']),
    ('allowances','allowance(address,address)','mapping(address => mapping(address => uint256))',['allowances','allowance']),
]

ERC721_STATE_VARIAVLES = [
    ('name','name()', 'string',  ['name']),
    ('symbol','symbol()', 'string',['symbol']),
    ('ownerOf','ownerOf(uint256)','mapping(uint256 => address)',['owners'],), # 这个owner不是管理员 owner
    ('balances','balanceOf(address)','mapping(address => uint256)',['balances','balance']),
    ('tokenApprovals','getApproved(uint256)','mapping(address => uint256)',['tokenapprovals','tokenapproval']),
    ('operatorApprovals','isApprovedForAll(address, address)','mapping(address => mapping(address => bool))',['operatorapprovals','operatorapproval']),
    ('uri','tokenURI(uint256)','string',['baseuri','uri'])
]
ERC1155_STATE_VARIAVLES = [
    ('balances','balanceOf(address, uint256)','mapping(uint256 => mapping(address => uint256))',['balances','balance']),
    ('operatorApprovals','isApprovedForAll(address, address)','mapping(address => mapping(address => bool))',['_operatorapprovals','operatorapproval']),
    ('uri','uri(uint256)','string',['uri']),
    ('totalSupply','totalSupply()', 'mapping(uint256 => uint256)', ['totalsupply','supply'])
]