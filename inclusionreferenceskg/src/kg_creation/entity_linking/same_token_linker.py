from collections import defaultdict
from functools import reduce

from kg_creation.entity_linking.entity_linker import EntityLinker
from kg_creation.knowledge_graph import KnowledgeGraph


class SameTokenLinker(EntityLinker):
    def link(self, graph: KnowledgeGraph) -> KnowledgeGraph:
        group_by_token = defaultdict(list)
        for node in graph.nodes.values():
            if hasattr(node.item, "token"):
                group_by_token[node.item.token].append(node.id)

        for nodes in group_by_token.values():
            reduce(graph.merge, nodes)

        return graph

