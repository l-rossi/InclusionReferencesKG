from functools import reduce

from spacy.matcher import Matcher
from spacy.tokens import Doc, Token

from document_parsing.node.node import Node
from document_parsing.node.node_traversal import pre_order
from kg_creation.entity_linking.entity_linker import EntityLinker
from kg_creation.knowledge_graph import KnowledgeGraph
from kg_creation.sentence_analysing.phrase import PhraseObject


class ReferenceLinker(EntityLinker):

    def __init__(self, doc: Doc, max_lookahead: int = 10):
        """
        An EntityLinker that links entities bound together by a "referenced in <reference>" expression.

        :param doc: The Doc object to operate on.
        :param max_lookahead: The maximum distance to look ahead when searching for references.
        """

        self.doc = doc
        self.matcher = Matcher(doc.vocab)

        self.max_lookahead = max_lookahead
        self.matcher.add("REF_IN", [[
            {},
            {"POS": "VERB"},
            {"POS": "ADP", "OP": "+"},
            {"TAG": "REF"}
        ], [
            {},
            {"POS": "ADJ"},
            {"POS": "ADP", "OP": "+"},
            {"TAG": "REF"}
        ]])

    def link(self, graph: KnowledgeGraph) -> KnowledgeGraph:

        n_resolved = 0
        n_tackled = 0

        for kg_node in list(graph.nodes.values()):
            if not isinstance(kg_node.item, PhraseObject):
                continue

            ind = kg_node.item.token.i
            span = self.doc[ind: ind + self.max_lookahead]
            matches = self.matcher(span)

            for _, start, end in matches:
                ref = span[end - 1]
                target_ids = set()
                for target in ref._.reference.targets:
                    for node in pre_order(target):
                        target_ids.add(node.id)

                kg_nodes_in_target = [node for node in graph.nodes.values() if
                                      not isinstance(node.item, Node) and
                                      node.item.token._.node.id in target_ids]

                nodes_to_be_merged = {n.id for n in kg_nodes_in_target if
                                      self._equals(n.item.token, kg_node.item.token)}

                if kg_node.item.token._.node.title == "GDPR":
                    n_tackled += 1
                    if nodes_to_be_merged:
                        n_resolved += 1

                reduce(graph.merge, nodes_to_be_merged, kg_node.id)

        print(n_resolved, n_tackled)
        return graph

    def _equals(self, tok1: Token, tok2: Token) -> bool:
        """
        Determines if two tokens refer to the same entity and should be merged.
        """

        t1 = (Doc.get_extension("coref_chains") and self.doc._.coref_chains.resolve(tok1)) or [tok1]
        t2 = (Doc.get_extension("coref_chains") and self.doc._.coref_chains.resolve(tok2)) or [tok2]

        return set(t.lemma for t in t1) == set(t.lemma for t in t2)
