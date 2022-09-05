
from typing import List
from slither.core.cfg.node import Node, NodeType
from slither.core.declarations import (
        Enum,
        Event,
        Modifier,
        EnumContract,
        StructureContract,
        FunctionContract,
        Function,
        SolidityVariable,
        SolidityVariableComposed,
)
from slither.slithir.variables import (
    Constant,
    LocalIRVariable,
    ReferenceVariable,
    StateIRVariable,
    TemporaryVariable,
    TupleVariable,
)

from slither.slithir.operations import (
    HighLevelCall,Index,InternalCall,EventCall,Length,LibraryCall,LowLevelCall,Member,OperationWithLValue,Phi,PhiCallback,SolidityCall,Return,Operation,Condition,Transfer)

from slither.core.variables.variable import Variable
from slither.core.variables.state_variable import StateVariable



from .condition_node import (get_require, get_if, ConditionNode)
from .node_naga import NodeN
from .variable_group import (VariableGroup, var_group_combine)

class FunctionN():
    def __init__(self, function: FunctionContract, cn):
        #self.__dict__.update(function.__dict__)
        self.cn = cn
        self.function:"FunctionContract" = function
        self._all_require_nodes:List["Node"] = None
        self._all_if_nodes:List["Node"] = None
        self._all_condition_nodes:List["Node"] = None

        self._require_conditions:List["ConditionNode"] = None
        self._if_conditions:List["ConditionNode"] = None
        self._conditions:List["ConditionNode"] = None

        self._owner_candidates:List["Variable"] = None
        self._events:List["EventCall"] = None
        self._return_nodes:List["Node"] = None
        self._return_var_group:"VariableGroup" = None

        self.params2agrs = _get_params2agrs(self.function) # 映射外部参数到 args
        self.andand_if_nodes:List["Node"] = []
        self.andand_require_nodes:List["Node"] = []

        #self.owners:List["Variable"] = [] # 如果不为空，则说明只能由 owner 写入
        #self._state_vars_read_in_requires:List["StateVariable"] = None
        #self._local_vars_read_in_requires = None
        #self._solidity_vars_read_in_requires:List["SolidityVariable"] = None

    @property
    def is_constructor_or_initializer(self) -> bool:
        return self.function.is_constructor or 'init' in str(self.function.name).lower() or 'constructor' in str(self.function.name).lower()


    @property
    def all_require_nodes(self) -> List["Node"]:
        if self._all_require_nodes is None:
            nodes = []
            for node in self.function.all_nodes():
                if any(
                    c.name in ["require(bool)", "require(bool,string)"]
                    for c in node.solidity_calls
                ):
                    nodes.append(node)
            self._all_require_nodes = nodes
        return self._all_require_nodes

    @property
    def all_if_nodes(self) -> List["Node"]:
        if self._all_if_nodes is None:
            nodes = []
            for node in self.function.all_nodes():
                if node.contains_if(False):
                    nodes.append(node)
            self._all_if_nodes = nodes
        return self._all_if_nodes

    
    @property
    def all_condition_nodes(self) -> List["Node"]:
        if self._all_condition_nodes is None:
            self._all_condition_nodes = self.all_require_nodes + self.all_if_nodes
        return self._all_condition_nodes

    @property
    def require_conditions(self) -> List["ConditionNode"]:
        if self._require_conditions is not None:
            return self._require_conditions
        self._require_conditions = []
        for node in self.all_require_nodes:
            self._require_conditions += get_require(node, self)
        return self._require_conditions

            
    @property
    def if_conditions(self) -> List["ConditionNode"]:
        if self._if_conditions is None:
            self._if_conditions = []
            for node in self.all_if_nodes:
                self._if_conditions += get_if(node, self)
        return self._if_conditions

    @property
    def conditions(self) -> List["ConditionNode"]:
        '''
        IF condition 由于语义问题，会带来大量的假阳性，所以我们不考虑 IF condition
        '''
        
        if self._conditions is None:
            self._conditions = self.require_conditions # + self.if_conditions
        return self._conditions
    
    @property
    def exist_oror_conditions(self) -> List["ConditionNode"]:
        exist_oror_conditions = []
        for condition in self.conditions:
            if condition.exist_oror:
                exist_oror_conditions.append(condition)
        return exist_oror_conditions

    @property
    def andand_condition_nodes(self)->List["Node"]:
        return self.andand_require_nodes + self.andand_if_nodes

    @property
    def owner_candidates(self) -> List["Variable"]:
        if self._owner_candidates is not None:
            return self._owner_candidates
        owner_candidates = []
        for cond in self.conditions:
            owner_candidates += cond.owner_candidates
        self._owner_candidates = list(set(owner_candidates))
        return self._owner_candidates

    @property
    def events(self) -> List["Event"]:
        if self._events is not None: return self._events

        self._events = []
        for ir in self.function.all_slithir_operations():
            if isinstance(ir, EventCall):
                self._events.append(ir)
        return self._events

    @property
    def return_nodes(self) -> List[NodeN]:
        if self._return_nodes is not None: return self._return_nodes
        self._return_nodes = []
        for node in self.function.nodes:
            if node.type == NodeType.RETURN:
                exp_node = NodeN(node)
                self._return_nodes.append(exp_node)
        return self._return_nodes

    @property
    def return_var_group(self) -> VariableGroup:
        if self._return_var_group is not None: return self._return_var_group

        self._return_var_group = var_group_combine([exp_node.dep_vars_groups for exp_node in self.return_nodes])
        return self._return_var_group

    def __str__(self) -> str:
        return self.function.name
    
    @property
    def name(self) -> str:
        return self.function.name

def _get_params2agrs(f):
        params2args = {} # 绑定参数和args
        for node in f.all_nodes():
            for ir in node.irs_ssa:
                if isinstance(ir, (InternalCall,HighLevelCall)):
                    if isinstance(ir.function,FunctionContract) and len(ir.arguments) <= len(ir.function.parameters):
                        for arg_index in range(0,len(ir.arguments)):
                            arg = ir.arguments[arg_index]
                            param = ir.function.parameters[arg_index]

                            if isinstance(arg,(StateIRVariable,LocalIRVariable)):
                                arg = arg._non_ssa_version
                            if isinstance(param,(StateIRVariable,LocalIRVariable)):
                                param = arg._non_ssa_version
                            params2args[param] = arg

        return params2args
