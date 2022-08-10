from __future__ import annotations

import warnings
from typing import Dict, Tuple, Union, Optional, Set

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

    def add_edge(self, u: str, v: str, label: str):
        """
        Creates an edge between from node u to node v. If either u or v does they are created
        as a node sans item. If the edge already exists, it is overwritten.

        :param label: The edge label.
        :param u: Id of the first node.
        :param v: Id of the second node.
        """
        if not self.nodes.get(u):
            self._add_node(u, None)
        if not self.nodes.get(v):
            self._add_node(v, None)

        self.nodes[u].adj[v] = (self.nodes[v], label)
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

    def merge(self, u: str, v: str, item: Optional[Union[Predicate, PhraseObject, Node]] = None):
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
            return

        if not v_node:
            warnings.warn(f"Could not merge nodes with ids {u} and {v} as node with id {v} does not exist.")
            return

        if not set.isdisjoint(u_node.adj_in, v_node.adj_in):
            warnings.warn(
                "Merging nodes with non-disjoint in-neighbours. The labels associated with node u will be kept")

        # Replace edges pointing at v
        for ref in v_node.adj_in:
            label = self.nodes[ref].adj[v][1]
            self.nodes[ref].adj.pop(v)
            if v != u:
                self.add_edge(ref, u, label=label)

        v_node.adj_in = []

        # Replace edges v points to
        for id_, (node, label) in v_node.adj.items():
            node.adj_in.remove(v)
            self.add_edge(u, id_, label)

        self.nodes.pop(v)

        if item is not None:
            u_node.item = item

        return u

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
            for _, (neighbor, label) in node.adj.items():
                out.edge(str(node.id), str(neighbor.id), label=label)

        return out


class KGNode:
    def __init__(self, id_: str, item: Optional[Union[Predicate, PhraseObject, Node]]):
        """
        :param id_: The id of the KGNode
        :param item: The item to store.
        """

        # The adjacency list (dictionary) stores a set of tuples of Node and edge label
        self.adj: Dict[str, Tuple[KGNode, str]] = dict()
        # A KGNode keeps a set of references of nodes that point to it (in-neighbours). This speeds up merging of nodes.
        self.adj_in: Set[str] = set()
        self.id = id_
        self.item = item

    def __str__(self) -> str:
        if isinstance(self.item, Predicate):
            return f"{self.item.token}, negated: {self.item.negated}, prepositions: {self.item.prepositions}"
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
