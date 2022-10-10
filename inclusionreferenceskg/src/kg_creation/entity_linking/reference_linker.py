from collections import defaultdict
from functools import reduce

from spacy.matcher import Matcher
from spacy.tokens import Doc, Token

from document_parsing.node.document import Document
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
        node_id_to_kg_nodes = defaultdict(list)
        for kg_node in graph.nodes.values():
            if not isinstance(kg_node.item, Node):
                node_id_to_kg_nodes[kg_node.item.token._.node.id].append(kg_node)

        for kg_node in graph.nodes.values():
            if not isinstance(kg_node.item, PhraseObject):
                continue

            ind = kg_node.item.token.i
            span = self.doc[ind: ind + self.max_lookahead]
            # We only consider the first match as to avoid situations where a conjunction would lead to
            # multiple matches
            matches = [x for x in self.matcher(span) if x[1] == 0]
            if not matches:
                continue

            _, start, end = matches[0]

            ref = span[end - 1]
            target_ids = set()
            for target in ref._.reference.targets:
                for node in pre_order(target):
                    target_ids.add(node.id)

            kg_nodes_in_target = [kn for id_ in target_ids if id_ in node_id_to_kg_nodes for kn in
                                  node_id_to_kg_nodes.get(id_)]

            nodes_to_be_merged = {n.id for n in kg_nodes_in_target if n.id != kg_node.id and
                                  self._equals(n.item.token, kg_node.item.token)}

            containing_document = kg_node.item.token._.node
            while containing_document.depth > Document.depth:
                containing_document = containing_document.parent

            reduce(graph.merge, nodes_to_be_merged, kg_node.id)

        return graph

    def _equals(self, tok1: Token, tok2: Token) -> bool:
        """
        Determines if two tokens refer to the same entity and should be merged.
        """

        t1 = (Doc.get_extension("coref_chains") and self.doc._.coref_chains.resolve(tok1)) or [tok1]
        t2 = (Doc.get_extension("coref_chains") and self.doc._.coref_chains.resolve(tok2)) or [tok2]

        return set(t.lemma for t in t1) == set(t.lemma for t in t2)
