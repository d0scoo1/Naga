import sys
sys.path.append(".")
from solc_utils import set_solc
from slither import Slither



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

from naga.core.function_exp import FunctionExp
from naga.core.contract_exp import ContractExp
from naga.core.require_node import *
from naga.core.type_compare import *
from naga.core.static_track import *
