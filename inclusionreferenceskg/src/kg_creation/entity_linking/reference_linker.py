import spacy.matcher
from spacy.matcher import Matcher
from spacy.tokens import Doc

from inclusionreferenceskg.src.kg_creation.entity_linking.entity_linker import EntityLinker
from inclusionreferenceskg.src.kg_creation.knowledge_graph import KnowledgeGraph
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import Predicate


class ReferenceLinker(EntityLinker):
    """
    An EntityLinker that links entities bound together by a "referenced in <Reference>" expression.
    """

    def __int__(self, doc: Doc):
        self.doc = doc

    def link(self, graph: KnowledgeGraph) -> KnowledgeGraph:


        # TODO implement
        for node in graph.nodes.values():
            if not isinstance(node.item, Predicate):
                continue

            item = node.item
            print(list(item.token.subtree))
            # print(matcher(item.token.))

        return graph
