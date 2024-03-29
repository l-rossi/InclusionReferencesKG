from __future__ import annotations

from kg_creation.attribute_extraction.attribute_extractor import AttributeExtractor
from kg_creation.knowledge_graph import KnowledgeGraph
from kg_creation.sentence_analysing.phrase import Predicate


class NegationExtractor(AttributeExtractor):
    """
    Tries to determine if a predicate is negated. Double negations cancel each other out.
    (This fails for some colloquial expressions, see the use of 'ain't')
    """

    def accept(self, graph: KnowledgeGraph) -> KnowledgeGraph:
        for node in graph.nodes.values():
            if isinstance(node.item, Predicate):
                negation_counter = sum(1 for tok in node.item.token.children if tok.dep_ == "neg")
                negation_counter += sum(
                    1 for tok in node.item.token.children if
                    tok.dep_ == "mark" and tok.pos_ == "SCONJ" and tok.text in {"except", "unless"})

                node.attributes["negated"] = negation_counter % 2 == 1

        return graph
