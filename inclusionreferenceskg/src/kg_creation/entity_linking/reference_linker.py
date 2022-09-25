from functools import reduce

from spacy.matcher import Matcher
from spacy.tokens import Doc, Token

from inclusionreferenceskg.src.document_parsing.node.node import Node
from inclusionreferenceskg.src.document_parsing.node.node_traversal import pre_order
from inclusionreferenceskg.src.kg_creation.entity_linking.entity_linker import EntityLinker
from inclusionreferenceskg.src.kg_creation.knowledge_graph import KnowledgeGraph
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import PhraseObject


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

        marked_for_merge = []

        for kg_node in graph.nodes.values():
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

                #print("span", span)
                #print("node token", kg_node.item.token)

                # TODO find more efficient implementation by precomputing

                kg_nodes_in_target = [node for node in graph.nodes.values() if
                                      not isinstance(node.item, Node) and node.item.token._.node.id in target_ids]
                # print("targes:", [graph.nodes.get(id) for id in target_ids])
                #print("kg_nodes_in_target", len(kg_nodes_in_target))

                nodes_to_be_merged = {n.id for n in kg_nodes_in_target if
                                      self._equals(n.item.token, kg_node.item.token)}
                #print("nodes_to_be_merged", len(nodes_to_be_merged))

                if nodes_to_be_merged:
                    marked_for_merge.append(nodes_to_be_merged | {kg_node.id})

        # We first group all the groups of nodes that should be merged by
        # intersection, i.e., if two or more groups of nodes intersect, they must all be merged as once.
        # We do this to avoid nodes being deleted by a merge which are then needed in a subsequent merge.

        # We amend the id sets by a tag that indicates if that group has been consumed by another.
        to_be_merged_stack = [[False, x] for x in marked_for_merge]
        to_be_merged_new = []

        while to_be_merged_stack:
            _, curr = to_be_merged_stack.pop()

            for consumed_and_nodes in to_be_merged_stack:
                if not curr.isdisjoint(consumed_and_nodes[1]):
                    consumed_and_nodes[0] = True
                    curr |= consumed_and_nodes[1]

            to_be_merged_stack = [[False, nodes]
                                  for consumed, nodes in to_be_merged_stack if not consumed]

        for nodes_to_be_merged in to_be_merged_new:
            reduce(graph.merge, nodes_to_be_merged)

        return graph

    def _equals(self, tok1: Token, tok2: Token) -> bool:
        """
        Determines if two tokens refer to the same entity and should be merged.
        """

        t1 = (Doc.get_extension("coref_chains") and self.doc._.coref_chains.resolve(tok1)) or [tok1]
        t2 = (Doc.get_extension("coref_chains") and self.doc._.coref_chains.resolve(tok2)) or [tok2]

        return set(t.lemma for t in t1) == set(t.lemma for t in t2)
