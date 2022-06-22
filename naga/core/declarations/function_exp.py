from typing import Dict, TYPE_CHECKING, List, Optional, Set, Union, Callable, Tuple
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

from slither.core.variables.variable import(
    Variable
)
from slither.slithir.operations.event_call import EventCall
from .require_exp import (get_requires,RequireExp,node_track)


class FunctionExp():
    def __init__(self, function: FunctionContract):
        #self.__dict__.update(function.__dict__)
        self.function:FunctionContract = function
        self._all_require_nodes:List[Node] = None
        self.requires:List[RequireExp] = self._get_requires()
        self.owner_candidates:List = self._get_owner_candidates()
        self.events = self._get_events()

        self.owners = [] # 如果不为空，则说明只能由 owner 写入
        self._state_vars_read_in_requires = None
        self._local_vars_read_in_requires = None
        self._solidity_vars_read_in_requires = None



    @property
    def all_require_nodes(self):
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

    def _get_requires(self):
        requires = []
        for node in self.all_require_nodes:
            requires += get_requires(node)
        return requires


    def _get_owner_candidates(self):
        owner_candidates = []
        for require in self.requires:
            owner_candidates += require.owner_candidates
        return owner_candidates

    def _get_events(self) -> List[Event]:
        events = []
        for ir in self.function.all_slithir_operations():
            if isinstance(ir, EventCall):
                events.append(ir)
        return events

    def _get_returns(self) -> List[Variable]:
        returns = []

        for node in self.function.nodes:
            if node.type == NodeType.RETURN:
                print(node)
                all_read_vars_group = node_track(node)
                print('--',all_read_vars_group)
          

                


    @property
    def state_vars_read_in_requires(self):
        if self._state_vars_read_in_requires is not None:
            return self._state_vars_read_in_requires
        
        self._state_vars_read_in_requires = []
        for exp_req in self.requires:
            self._state_vars_read_in_requires += exp_req.all_read_vars_group.state_vars
        return self._state_vars_read_in_requires
    
    @property
    def local_vars_read_in_requires(self):
        if self._local_vars_read_in_requires is not None:
            return self._local_vars_read_in_requires
        
        self._local_vars_read_in_requires = []
        for exp_req in self.requires:
            self._local_vars_read_in_requires += exp_req.all_read_vars_group.local_vars
        return self._local_vars_read_in_requires

    @property
    def solidity_vars_read_in_requires(self):
        if self._solidity_vars_read_in_requires is not None:
            return self._solidity_vars_read_in_requires
        
        self._solidity_vars_read_in_requires = []
        for exp_req in self.requires:
            self._solidity_vars_read_in_requires += exp_req.all_read_vars_group.solidity_vars
        return self._solidity_vars_read_in_requires

    def __str__(self) -> str:
        return self.function.name
    '''
    def set_only_owner(self, only_owner: bool):
        self._only_owner = only_owner
    
    @property
    def is_only_owner(self):
        return self._only_owner
    '''





'''
def _search_related_nodes(node:Node)->List[Node]:
    """
        遍历一个node的所有父节点，如果父节点 lvalue 包含了子节点的 rvalue，则认为两者相关
        args:
            node: the node to search
        return:
            a list of nodes that are related to the node
    """
    
    # 往上寻找到所有 father nodes
    to_explore = node.fathers
    father_nodes = []
    while to_explore:
        n = to_explore.pop(0)
        if n in father_nodes:
            continue
        father_nodes.append(n)
        to_explore += n.fathers

    #print('Search Nodes')
    #print(father_nodes)

    nodes_ssa_variables_read = node.ssa_variables_read  # 我们不断的往上探索，找到所有的读写依赖关系
    nodes_ssa_variables_read.reverse()
    
    values = [node]

    while nodes_ssa_variables_read and father_nodes:
        """
        目前是按顺序检索，如果有必要，可以改成遍历，直到遍历失败
        """
        n = father_nodes.pop(0)
        #print('father ----',n,n.ssa_variables_read)

        if any(ssa_var in n.ssa_variables_written for ssa_var in nodes_ssa_variables_read):
            values.append(n)

            nodes_ssa_variables_read = list(set(nodes_ssa_variables_read)-set(n.ssa_variables_written)) #

            ssa_read = n.ssa_variables_read
            ssa_read.reverse()
            nodes_ssa_variables_read += ssa_read
    return values

def __search_all_related_nodes(node:Node)->List[Node]:
    values = _search_related_nodes(node)
    to_explore =[]
    for node in values:
        #print('--',node)
        to_explore += [ c for c in node.internal_calls if isinstance(c, Function) ]
        to_explore += [c for (_, c) in node.library_calls if isinstance(c, Function)] 

    for c in to_explore:
        if isinstance(c, Function):
            #print('---',c.name)
            values += _explore_functions(c, lambda f:f.nodes)

    
    return values


def _explore_functions(fun: Function, f_new_values: Callable[["Function"], List]):

    values = f_new_values(fun)
    explored = [fun]
    to_explore = [
        c for c in fun.internal_calls if isinstance(c, Function) and c not in explored
    ]
    to_explore += [
        c for (_, c) in fun.library_calls if isinstance(c, Function) and c not in explored
    ]
    to_explore += [m for m in fun.modifiers if m not in explored]

    while to_explore:
        f = to_explore.pop(0)
        if f in explored:
            continue
        explored.append(f)

        values += f_new_values(f)

        to_explore += [
            c
            for c in f.internal_calls
            if isinstance(c, Function) and c not in explored and c not in to_explore
        ]
        to_explore += [
            c
            for (_, c) in f.library_calls
            if isinstance(c, Function) and c not in explored and c not in to_explore
        ]
        to_explore += [m for m in f.modifiers if m not in explored and m not in to_explore]

    #return list(set(values))
    return values
'''