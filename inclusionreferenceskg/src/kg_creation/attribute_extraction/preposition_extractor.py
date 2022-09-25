from inclusionreferenceskg.src.kg_creation.attribute_extraction.attribute_extractor import AttributeExtractor
from inclusionreferenceskg.src.kg_creation.knowledge_graph import KnowledgeGraph
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import Predicate


class PrepositionExtractor(AttributeExtractor):

    def accept(self, graph: KnowledgeGraph) -> KnowledgeGraph:
        for node in graph.nodes.values():
            if not isinstance(node.item, Predicate):
                continue

            for adj, label, attributes in node.adj.values():
                if label != "agent" and label != "patient":
                    continue

                if hasattr(adj.item, "token") and adj.item.token.head.dep_ == "prep":
                    if attributes.get("prepositions") is None:
                        attributes["prepositions"] = []
                    attributes["prepositions"].append(adj.item.token.head.text)

        return graph
