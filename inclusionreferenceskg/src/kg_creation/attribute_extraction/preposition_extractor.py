from kg_creation.attribute_extraction.attribute_extractor import AttributeExtractor
from kg_creation.knowledge_graph import KnowledgeGraph
from kg_creation.sentence_analysing.phrase import Predicate


class PrepositionExtractor(AttributeExtractor):
    """
    Extractor to extract more information on labels, specifically
    the preposition and in some cases the adjective complement.

    Note: Something could be done about dative constructs and phrasal verb particles.
    Though not strictly prepositions, they fulfill a similar role.
    """

    prepositional_dependencies = {"prep", "acomp"}

    def accept(self, graph: KnowledgeGraph) -> KnowledgeGraph:
        for node in graph.nodes.values():
            if not isinstance(node.item, Predicate):
                continue

            for adj, label, attributes in node.adj.values():
                if label != "agent" and label != "patient":
                    continue

                if hasattr(adj.item,
                           "token") and adj.item.token.head.dep_ in PrepositionExtractor.prepositional_dependencies:
                    if attributes.get("prepositions") is None:
                        attributes["prepositions"] = []

                    prep_chain = [adj.item.token.head]
                    while prep_chain[0].head.dep_ in PrepositionExtractor.prepositional_dependencies:
                        prep_chain.insert(0, prep_chain[0].head)

                    attributes["prepositions"].extend(prep_chain)

        return graph
