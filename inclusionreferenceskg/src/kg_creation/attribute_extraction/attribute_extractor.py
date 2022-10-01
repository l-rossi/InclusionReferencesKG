from abc import abstractmethod, ABC

from kg_creation.knowledge_graph import KnowledgeGraph


class AttributeExtractor(ABC):
    @abstractmethod
    def accept(self, graph: KnowledgeGraph) -> KnowledgeGraph:
        """
        An AttributeExtractor works on the graph level augmenting the graph and
        returning either a new graph or the modified graph.

        This is not a pure function.

        :param graph:
        :return:
        """
        raise NotImplementedError()
