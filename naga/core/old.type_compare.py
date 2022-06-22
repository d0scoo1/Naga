from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.mapping_type import MappingType

def is_owner_type(v):
    """
        判断是否为 owner 的类型
    """
    if v.type == ElementaryType('address'):
        return True
    if isinstance(v.type, MappingType) and v.type.type_from == ElementaryType('address'):
        return True
    return False

from slither.core.declarations import SolidityVariableComposed
def is_msg_sender(v):
    """
        判断是否为 msg.sender 类型
    """
    return v == SolidityVariableComposed('msg.sender')