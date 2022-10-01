from abc import ABC, abstractmethod

from kg_creation.knowledge_graph import KnowledgeGraph


class EntityLinker(ABC):
    """
    ABC for the parts in the pipeline responsible for linking/merging nodes of the knowledge graph.
    """

    @abstractmethod
    def link(self, graph: KnowledgeGraph) -> KnowledgeGraph:
        """
        Accepts a graph, links nodes according to the class's rules and then returns the graph again.

        :param graph: The graph for which to link nodes.
        :return: The accepted graph, now with linked nodes.
        """
        raise NotImplementedError()
