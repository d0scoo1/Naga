import sys
sys.path.append(".")
from solc_utils import set_solc
from slither import Slither
from tqdm import tqdm
import os
import json
import time


from slither.slithir.operations import (
    HighLevelCall,
    Index,
    InternalCall,
    Length,
    LibraryCall,
    LowLevelCall,
    Member,
    OperationWithLValue,
    Phi,
    PhiCallback,
    SolidityCall,
    Return,
    Operation,
)

from slither.slithir.variables import (
    Constant,
    LocalIRVariable,
    ReferenceVariable,
    StateIRVariable,
    TemporaryVariable,
    TupleVariable,
)
from slither.core.variables.state_variable import StateVariable



from slither.core.declarations import (
    SolidityVariableComposed,
    Contract,
    Function,
    Modifier
)

from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.mapping_type import MappingType


