from __future__ import annotations

from inclusionreferenceskg.src.kg_creation.attribute_extraction.attribute_extractor import AttributeExtractor
from inclusionreferenceskg.src.kg_creation.knowledge_graph import KnowledgeGraph
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import Predicate


class NegationExtractor(AttributeExtractor):

    def accept(self, graph: KnowledgeGraph) -> KnowledgeGraph:
        for node in graph.nodes.values():
            if isinstance(node.item, Predicate):
                node.item.negated = sum(1 for tok in node.item.token.children if tok.dep_ == "neg") % 2 == 1

        return graph
