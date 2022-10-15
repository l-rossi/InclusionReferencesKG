import logging
import warnings
from functools import reduce
from typing import Dict

from spacy.tokens import Token

from kg_creation.entity_linking.entity_linker import EntityLinker
from kg_creation.knowledge_graph import KnowledgeGraph, KGNode
from kg_creation.sentence_analysing.phrase import Predicate


class RelativeClauseLinker(EntityLinker):

    def __init__(self):
        warnings.warn("RelativeClauseLinker is deprecated as its function is now done by the Phrase Extractor directly",
                      DeprecationWarning)

    def link(self, graph: KnowledgeGraph) -> KnowledgeGraph:

        token_to_node: Dict[Token, KGNode] = {node.item.token: node for node in graph.nodes.values() if
                                              hasattr(node.item, "token")}

        for node in list(graph.nodes.values()):
            if isinstance(node.item, Predicate) and node.item.token.dep_ == "relcl":
                predicate_node_for_merge = [node] + [token_to_node[tok] for tok in node.item.token.children if
                                                     tok.dep_ == "conj"]

                relative_pronoun_nodes = []
                for pred in predicate_node_for_merge:
                    relative_pronoun_nodes += [neighbour.id for neighbour, label, _ in pred.adj.values() if
                                               label == "agent" and neighbour.item.token.pos_ == "PRON"]

                if relative_pronoun_nodes:
                    if node.item.token.head not in token_to_node:
                        logging.warning(f"Tried to merge relative pronoun into an "
                                        f"object node that does not exist: '{node.item.token.head}'.")
                    else:
                        reduce(graph.merge, relative_pronoun_nodes, token_to_node[node.item.token.head].id)

        return graph
