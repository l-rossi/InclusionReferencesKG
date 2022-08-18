import itertools
import uuid
import warnings
from typing import List, Tuple

import coreferee
import spacy
from spacy import Language
from spacy.matcher import Matcher
from spacy.tokens import Token, Doc

from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.article import Article
from inclusionreferenceskg.src.document_parsing.node.node import Node
from inclusionreferenceskg.src.document_parsing.node.node_traversal import pre_order
from inclusionreferenceskg.src.document_parsing.node.paragraph import Paragraph
from inclusionreferenceskg.src.kg_creation.attribute_extraction.negation_extractor import NegationExtractor
from inclusionreferenceskg.src.kg_creation.attribute_extraction.preposition_extractor import PrepositionExtractor
from inclusionreferenceskg.src.kg_creation.entity_linking.reference_linker import ReferenceLinker
from inclusionreferenceskg.src.kg_creation.entity_linking.relative_clause_linker import RelativeClauseLinker
from inclusionreferenceskg.src.kg_creation.entity_linking.same_lemma_in_same_article_linker import \
    SameLemmaInSameArticleLinker
from inclusionreferenceskg.src.kg_creation.knowledge_graph import KnowledgeGraph
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import Phrase
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase_extractor import PhraseExtractor
from inclusionreferenceskg.src.reference_detection.regex_reference_detector import RegexReferenceDetector
from inclusionreferenceskg.src.reference_resolution.reference_resolver import ReferenceResolver
from inclusionreferenceskg.src.util.parser_util import gdpr_dependency_root
from inclusionreferenceskg.src.util.spacy_components import REFERENCE_QUALIFIER_RESOLVER_COMPONENT


class KGRenderer:
    """
    Translates the graph from the internal format to a format used by external libraries for analysing and visualisation.
    """

    def render(self, root, phrases: List[Phrase]) -> KnowledgeGraph:
        graph = KnowledgeGraph()

        # add document structure:
        for node in pre_order(root):
            graph.add_node(node.id, node)

        for node in pre_order(root):
            for child in node.children:
                graph.add_edge(node.id, child.id, label="contains")

        for phrase in phrases:
            self._add_phrase(graph, phrase)

        return graph

    def _add_phrase(self, graph: KnowledgeGraph, phrase: Phrase):

        for predicate in phrase.predicate:
            graph.add_edge(predicate.token._.node.id, predicate.id, "defines")

        for predicate in phrase.predicate:
            graph.add_node(predicate.id, predicate)

        for patient_object in phrase.patient_objects:
            if patient_object.token._.reference and (targets := patient_object.token._.reference.targets):
                for target, predicate in itertools.product(targets, phrase.predicate):
                    graph.add_edge(predicate.id, target.id, "patient")
                    graph.add_node(target.id, target)
            else:
                graph.add_node(patient_object.id, patient_object)
                for predicate in phrase.predicate:
                    graph.add_edge(predicate.id, patient_object.id, "patient")

        for agent_object in phrase.agent_objects:
            if agent_object.token._.reference and (targets := agent_object.token._.reference.targets):
                for target, predicate in itertools.product(targets, phrase.predicate):
                    graph.add_edge(predicate.id, target.id, "agent")
                    graph.add_node(target.id, target)
            else:
                graph.add_node(agent_object.id, agent_object)
                for predicate in phrase.predicate:
                    graph.add_edge(predicate.id, agent_object.id, "agent")

        for patient_phrase in phrase.patient_phrases:
            for my_pred, other_pred in itertools.product(phrase.predicate, patient_phrase.predicate):
                graph.add_edge(my_pred.id, other_pred.id, "patient")
            self._add_phrase(graph, patient_phrase)

        for agent_phrase in phrase.agent_phrases:
            for my_pred, other_pred in itertools.product(phrase.predicate, agent_phrase.predicate):
                graph.add_edge(my_pred.id, other_pred.id, "agent")
            self._add_phrase(graph, agent_phrase)

        for conditional_phrase in phrase.condition_phrases:
            for my_pred, other_pred in itertools.product(phrase.predicate, conditional_phrase.predicate):
                graph.add_edge(my_pred.id, other_pred.id, "conditional")
            self._add_phrase(graph, conditional_phrase)


def nlp_doc(reference_base: Node, analyzed: Node, nlp: Language) -> Doc:
    """
    Creates a Spacy Doc from a Language object and does some initial setup.

    The main reason for not using a pipe component for this process is that we need to create
    the Doc object from only the main text of the GDPR whilst ignoring titles and the likes.


    :param reference_base: The document root from which to resolve references.
    :param analyzed: The document root node to be applied to the nlp.
    :param nlp: The Language object/pipe to be used.
    :return: A Doc made of the text content of the document supplied by the analyzed parameter. Tokens are supplied \
    with the part of the document they are a part of and the document is supplied with the base root.
    """

    if not Token.get_extension("node"):
        Token.set_extension("node", default=None)

    if not Doc.get_extension("document_structure"):
        # The root of this document.
        Doc.set_extension("document_structure", default=None)

    if not Doc.get_extension("reference_base"):
        # The root from where to resolve references.
        Doc.set_extension("reference_base", default=None)

    raw_text = ""
    # We keep a list of node content end positions in the text
    text_positions: List[Tuple[int, Node]] = []

    for node in pre_order(analyzed):
        raw_text += node.content
        raw_text += "\n"
        text_positions.append((len(raw_text), node))

    # We create an anonymous pipe to insert attributes into the doc right after creation.
    # TODO: This is bad practice and a better solution should ideally be found
    comp_name = "document_supplement_component_" + str(uuid.uuid4())

    @Language.component(comp_name)
    def comp(d):
        d._.document_structure = analyzed
        d._.reference_base = reference_base

        for tok in d:
            for pos, node in text_positions:
                if tok.idx < pos:
                    tok._.node = node
                    break
            else:
                warnings.warn(f"Could not assign a node to token '{tok}'. This is most likely caused by a bug.")

        return d

    nlp.add_pipe(comp_name, first=True)

    doc = nlp(raw_text)

    return doc


def main():
    # We need to use coreferee so that PyCharm does not tidy up the reference.
    if not coreferee:
        print("Could not import coreferee for anaphora resolution.")

    spacy.prefer_gpu()

    gdpr, document_root = gdpr_dependency_root()
    article6 = gdpr.resolve_loose([Article(number=49), Paragraph(number=1)])[0]

    root = document_root
    analyzed = gdpr

    attribute_extractors = {
        PrepositionExtractor(),
        NegationExtractor()
    }

    Token.set_extension("reference", default=None)
    # nlp = spacy.load("en_core_web_trf", disable=["ner"])
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    # nlp.add_pipe(DocumentTreeParser.SPACY_COMPONENT_NAME, config={}, after="tagger")
    nlp.add_pipe("coreferee", config={}, after="parser")
    nlp.add_pipe(RegexReferenceDetector.SPACY_COMPONENT_NAME, config={}, after="parser")
    nlp.add_pipe(ReferenceResolver.SPACY_COMPONENT_NAME, config={},
                 after=RegexReferenceDetector.SPACY_COMPONENT_NAME)
    nlp.add_pipe(REFERENCE_QUALIFIER_RESOLVER_COMPONENT, config={},
                 after=ReferenceResolver.SPACY_COMPONENT_NAME)

    doc = nlp_doc(root, analyzed, nlp)

    phrases = []
    phrase_extractor = PhraseExtractor()
    for sent in doc.sents:
        phrases.extend(phrase_extractor.extract_from_sentence(sent))

    for phrase in phrases:
        for attribute_extractor in attribute_extractors:
            attribute_extractor.accept_with_children(phrase)

    """graph, node_labels, edge_labels, node_colors = KGRenderer().render_to_networkx(root=analyzed, phrases=phrases)

    pos = nx.drawing.nx_agraph.graphviz_layout(graph)
    nx.draw(graph, pos=pos, labels=node_labels, with_labels=True, node_color=node_colors)
    nx.draw_networkx_edge_labels(graph, pos=pos, edge_labels=edge_labels)"""

    graph = KGRenderer().render(analyzed, phrases)

    # Test merging a bunch of nodes
    """f_id = None
    for kg_id in list(graph.nodes.keys()):
        kg_node = graph.nodes.get(kg_id)
        if not kg_node:
            continue

        if isinstance(kg_node.item, PhraseObject):
            if kg_node.item.token.lemma_ == "transfer":
                if f_id:
                    graph.merge(f_id, kg_node.id)
                else:
                    f_id = kg_node.id"""

    # graph = SameLemmaInSameArticleLinker(doc).link(graph)
    # graph = RelativeClauseLinker().link(graph)
    graph = ReferenceLinker(doc).link(graph)


    #graph.as_graphviz_graph("GDPR", engine="dot", format_="svg", attrs={"overlap": "true"}) \
    #    .render(directory='output/graphs', view=False)

    # for phrase in phrases:
    #    phrase.pprint()

    # plt.show()


if __name__ == "__main__":
    main()
