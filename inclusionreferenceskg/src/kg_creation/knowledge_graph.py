from __future__ import annotations

import warnings
from collections import defaultdict
from functools import reduce
from typing import Dict, Tuple, Union, Optional, Set, List

import graphviz
import networkx as nx

from inclusionreferenceskg.src.document_parsing.node.node import Node
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import PhraseObject, Predicate


class KnowledgeGraph:
    """
    A lightweight DiGraph representation. Specialized for interfacing with the rest of this codebase.
    A method for converting this representation to a Graphviz Graph are provided.
    """

    def __init__(self):
        self.nodes: Dict[str, KGNode] = dict()

    def add_edge(self, u: str, v: str, label: str, attributes: Dict[str, any] = None):
        """
        Creates an edge between from node u to node v. If either u or v does they are created
        as a node sans item. If the edge already exists, it is overwritten.

        :param label: The edge label.
        :param u: Id of the first node.
        :param v: Id of the second node.
        :param attributes: A dictionary of attributes / properties for the edge.
        """

        if attributes is None:
            attributes = dict()

        if not self.nodes.get(u):
            self._add_node(u, None)
        if not self.nodes.get(v):
            self._add_node(v, None)

        self.nodes[u].adj[v] = (self.nodes[v], label, attributes)
        self.nodes[v].adj_in.add(u)

    def _add_node(self, id_: str, item: Optional[Union[Predicate, PhraseObject, Node]]):
        """
        Private method for adding nodes allowing for None items. This API is not exposed as setting having a None item
        is usually undesirable.
        """
        if self.nodes.get(id_):
            self.nodes[id_].item = item
        else:
            self.nodes[id_] = KGNode(id_=id_, item=item)

    def add_node(self, id_: str, item: Union[Predicate, PhraseObject, Node]):
        """
        Creates a node for the given id containing 'item'. If a node with this id already exists, its item is updated.
        :param id_: The id of the node.
        :param item: The item to be held in the node.
        """
        self._add_node(id_, item)

    def merge(self, u: str, v: str):
        """
        Merges node v into node u. Edges from u to v or vice versa are lost.

        :param u: The id of the first node.
        :param v: The id of the second node.
        :param item: The new item of the merged node. If None, the item of vert u is used.
        :return: u (as to enable simple use of reduce).
        """

        u_node = self.nodes.get(u)
        v_node = self.nodes.get(v)
        if not u_node:
            warnings.warn(f"Could not merge nodes with ids {u} and {v} as node with id {u} does not exist.")
            return v

        if not v_node:
            warnings.warn(f"Could not merge nodes with ids {u} and {v} as node with id {v} does not exist.")
            return u

        if not set.isdisjoint(u_node.adj_in, v_node.adj_in):
            warnings.warn(
                "Merging nodes with non-disjoint in-neighbours. The labels associated with node u will be kept")

        doc = u_node.item.token.doc
        print(
            f"merging '{doc[u_node.item.token.i - 5:u_node.item.token.i + 5]}' and '{doc[v_node.item.token.i - 5:v_node.item.token.i + 5]}'")

        # Replace edges pointing at v
        for ref in v_node.adj_in:
            label, attributes = self.nodes[ref].adj[v][1:3]
            self.nodes[ref].adj.pop(v)
            if v != u:
                self.add_edge(ref, u, label=label, attributes=attributes)

        v_node.adj_in = []

        # Replace edges v points to
        for id_, (node, label, attributes) in v_node.adj.items():
            node.adj_in.remove(v)
            self.add_edge(u, id_, label, attributes)

        self.nodes.pop(v)

        print(f"merged {u} and {v}")
        return u

    @staticmethod
    def _edge_to_str(label, attributes: Dict[str, any]) -> str:
        return f"{label} [{(', '.join(f'{k}: {str(v)}' for k, v in attributes.items()))}]"

    def as_graphviz_graph(self, name: str, engine: str, format_: str, attrs: Dict[str, str]) -> graphviz.Digraph:
        """
        Produces a graphviz.Digraph from the nodes and edges in this graph.
        Treat the returned Graph as a read-only graph.

        :param name: The name of the graphviz graph.
        :param engine: The dot engine to use.
        :param format_: The format of the graph.
        :param attrs: Additional attributes passed to the graph_attr dict.
        :return: A graphviz.Digraph created from this KnowledgeGraph.
        """

        out = graphviz.Digraph(name, engine=engine, format=format_)
        out.graph_attr.update(attrs)

        for node in self.nodes.values():
            out.node(str(node.id), str(node))
            for _, (neighbor, label, attributes) in node.adj.items():
                out.edge(str(node.id), str(neighbor.id), label=KnowledgeGraph._edge_to_str(label, attributes))

        return out


class KGProxy(KnowledgeGraph):
    """
    Proxy for merging nodes in which merges are not applied directly.
    """

    def __init__(self, kg: KnowledgeGraph):
        super().__init__()
        self.nodes = kg.nodes
        self.merges: List[Tuple[str, str]] = []

    def merge(self, u: str, v: str):
        self.merges.append((u, v))
        return u


class BatchedMerge:
    """
    Creates a proxy around a knowledge graph to batch merging.
    """

    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg
        self.proxy_kg = KGProxy(kg)
        pass

    def __enter__(self) -> KGProxy:
        return self.proxy_kg

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Nodes are grouped so that no node is merged in more than one group.
        # We group by using a tree search algorithm on nodes until all nodes have been visited.
        nodes = set(x for edge in self.proxy_kg.merges for x in edge)
        groups = []

        adj: Dict[str, Set[str]] = defaultdict(set)
        for u, v in self.proxy_kg.merges:
            adj[u].add(v)
            adj[v].add(u)
        while nodes:
            curr = nodes.pop()
            group = {curr}

            search_stack = [curr]
            while search_stack:
                curr_search = search_stack.pop()
                for neighbour in adj[curr_search]:
                    if neighbour in nodes:
                        search_stack.append(neighbour)
                        group.add(neighbour)
                        nodes.discard(neighbour)

            groups.append(group)

        for group in groups:
            reduce(self.kg.merge, group)


class KGNode:
    def __init__(self, id_: str, item: Optional[Union[Predicate, PhraseObject, Node]]):
        """
        :param id_: The id of the KGNode
        :param item: The items to store. A KGNode should be created with only one item but through merging
        more items may be added.
        """

        # The adjacency list (dictionary) stores a set of tuples of Node and edge label
        self.adj: Dict[str, Tuple[KGNode, str, Dict[str, any]]] = dict()
        # A KGNode keeps a set of references of nodes that point to it (in-neighbours). This speeds up merging of nodes.
        self.adj_in: Set[str] = set()
        self.id = id_
        self.item = item

    def __str__(self) -> str:
        if isinstance(self.item, Predicate):
            return f"{self.item.token}, negated: {self.item.negated}"
        elif isinstance(self.item, PhraseObject):
            return self.item.pretty_str()
        elif isinstance(self.item, Node):
            return str(self.item.immutable_view())
        elif self.item is None:
            # TODO: Should probably raise an exception.
            return "NONE VALUE"
        else:
            raise ValueError(f"self.item has the wrong type. "
                             f"Expected one of Predicate, PhraseObject, Node. Was: '{type(self.item)}'.")


if __name__ == "__main__":
    G = nx.DiGraph()

    G.add_edge("1", "2")
