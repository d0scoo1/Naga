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
from .require_node import (get_requireNodes,RequireNode)
from .static_track import (node_track)

class FunctionExp():
    def __init__(self, function: FunctionContract):
        #self.__dict__.update(function.__dict__)
        self.function = function
        self._all_require_nodes = None
        self._requireNodes = None
        self._only_owner = False

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

    @property
    def requireNodes(self):
        if self._requireNodes is None:
            self._requireNodes = []
            for node in self.all_require_nodes:
                self._requireNodes += get_requireNodes(node)
        return self._requireNodes

    def set_only_owner(self, only_owner: bool):
        self._only_owner = only_owner
    
    @property
    def is_only_owner(self):
        return self._only_owner



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
