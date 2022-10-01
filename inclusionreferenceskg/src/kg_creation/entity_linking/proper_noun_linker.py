from collections import defaultdict
from functools import reduce
from tokenize import Token
from typing import Tuple, List

from kg_creation.entity_linking.entity_linker import EntityLinker
from kg_creation.knowledge_graph import KnowledgeGraph
from kg_creation.sentence_analysing.phrase import PhraseObject


class ProperNounLinker(EntityLinker):
    def link(self, graph: KnowledgeGraph) -> KnowledgeGraph:
        proper_nouns: List[Tuple[str, Tuple[Token, ...]]] = [
            (node.id,
             (node.item.token.text,) + tuple(tok.text for tok in node.item.token.children if tok.dep_ == "compound"))
            for node in graph.nodes.values() if isinstance(node.item, PhraseObject) and node.item.token.pos_ == "PROPN"
        ]

        group_by = defaultdict(list)
        for id, pn in proper_nouns:
            group_by[pn].append(id)

        for group in group_by.values():
            if len(group) > 1:
                reduce(graph.merge, group)

        return graph
