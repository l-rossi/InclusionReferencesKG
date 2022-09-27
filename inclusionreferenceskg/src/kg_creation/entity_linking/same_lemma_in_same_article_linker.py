from collections import defaultdict
from functools import reduce

from spacy.tokens import Doc

from inclusionreferenceskg.src.document_parsing.node.paragraph import Paragraph
from inclusionreferenceskg.src.kg_creation.entity_linking.entity_linker import EntityLinker
from inclusionreferenceskg.src.kg_creation.knowledge_graph import KnowledgeGraph
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import PhraseObject


class SameLemmaInSameParagraphLinker(EntityLinker):
    """
    Links nodes on the heuristic, that if a node is in the same paragraph and has the same lemma, it
    refers to the same thing.
    """

    def __init__(self, doc: Doc):
        self.doc = doc

    def link(self, graph: KnowledgeGraph) -> KnowledgeGraph:

        # TODO Do not merge nodes like 'which' (maybe only nouns)

        coref_chains = self.doc._.coref_chains if Doc.get_extension("coref_chains") else None

        group_by_paragraph = defaultdict(list)
        for kg_node in graph.nodes.values():
            if not isinstance(kg_node.item, PhraseObject):
                continue

            doc_node = kg_node.item.token._.node

            if doc_node.depth < Paragraph.depth:
                continue

            para = doc_node
            while doc_node is not None and para.depth > Paragraph.depth:
                para = para.parent

            group_by_paragraph[para.id].append(kg_node)

        for kg_nodes in group_by_paragraph.values():
            group_by_token_lemma = defaultdict(list)

            for kg_node in kg_nodes:
                base = kg_node.item.token
                if coref_chains and (res := coref_chains.resolve(base)):
                    base = res

                group_by_token_lemma[(base.lemma_, base.tag_)].append(kg_node.id)

            for group in group_by_token_lemma.values():
                reduce(graph.merge, group)

        return graph
