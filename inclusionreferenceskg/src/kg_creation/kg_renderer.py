import itertools
import logging
import uuid
from typing import List, Tuple, Set, Callable

import coreferee
import spacy
from spacy import Language
from spacy.tokens import Token, Doc

from document_parsing.node.node import Node
from document_parsing.node.node_traversal import pre_order
from kg_creation.attribute_extraction.attribute_extractor import AttributeExtractor
from kg_creation.attribute_extraction.negation_extractor import NegationExtractor
from kg_creation.attribute_extraction.preposition_extractor import PrepositionExtractor
from kg_creation.entity_linking.entity_linker import EntityLinker
from kg_creation.entity_linking.proper_noun_linker import ProperNounLinker
from kg_creation.entity_linking.reference_linker import ReferenceLinker
from kg_creation.entity_linking.same_lemma_in_same_paragraph_linker import \
    SameLemmaInSameParagraphLinker
from kg_creation.entity_linking.same_token_linker import SameTokenLinker
from kg_creation.knowledge_graph import KnowledgeGraph, BatchedMerge
from kg_creation.sentence_analysing.phrase import Phrase
from kg_creation.sentence_analysing.phrase_extractor import PhraseExtractor
from reference_detection.regex_reference_detector import RegexReferenceDetector
from reference_resolution.reference_resolver import ReferenceResolver
from util.spacy_components import REFERENCE_QUALIFIER_RESOLVER_COMPONENT


class KGRenderer:
    """
    Assembles an instance of KnowledgeGraph.
    """

    def render(self, root: Node, phrases: List[Phrase], include_extensions: bool = False) -> KnowledgeGraph:
        """
        Creates a graph from the a list of phrases and a document structure.

        :param root: The root node to use for the document structure.
        :param phrases: The phrases to be used to fill the content of the KG.
        :param include_extensions: Determines if the extension relationships 'of' and 'described_by' should be added.
        """
        graph = KnowledgeGraph()

        # We keep track of which phrases have already been added to avoid recursion errors.
        added_phrases = set()

        # add document structure:
        for node in pre_order(root):
            graph.add_node(node.id, node)

        for node in pre_order(root):
            for child in node.children:
                graph.add_edge(node.id, child.id, label="contains")

        for phrase in phrases:
            self._add_phrase(graph, phrase, added_phrases, include_extensions, topmost=True)

        return graph

    def _add_phrase(self, graph: KnowledgeGraph, phrase: Phrase, added_phrases: Set[str],
                    include_extensions: bool = False, topmost=False):
        if phrase.id in added_phrases:
            return
        added_phrases.add(phrase.id)

        if topmost:
            for predicate in phrase.predicate:
                graph.add_edge(predicate.token._.node.id, predicate.id, "defines")

        for predicate in phrase.predicate:
            graph.add_node(predicate.id, predicate)

        for patient_object in phrase.patient_objects:
            if patient_object.token._.reference and (targets := patient_object.token._.reference.targets):
                for target, predicate in itertools.product(targets, phrase.predicate):
                    graph.add_edge(predicate.id, target.id, "patient")
                    if target.id not in graph.nodes:
                        graph.add_node(target.id, target)
            else:
                graph.add_node(patient_object.id, patient_object)
                for predicate in phrase.predicate:
                    graph.add_edge(predicate.id, patient_object.id, "patient")

        for agent_object in phrase.agent_objects:
            if agent_object.token._.reference and (targets := agent_object.token._.reference.targets):
                for target, predicate in itertools.product(targets, phrase.predicate):
                    graph.add_edge(predicate.id, target.id, "agent")
                    if target.id not in graph.nodes:
                        graph.add_node(target.id, target)
            else:
                graph.add_node(agent_object.id, agent_object)
                for predicate in phrase.predicate:
                    graph.add_edge(predicate.id, agent_object.id, "agent")

        if include_extensions:
            possessor_stack = list(itertools.chain(phrase.agent_objects, phrase.patient_objects))
            # We assume that there are no circular dependencies in possessors.
            # This holds if possessors were created using PhraseExtractor.
            while possessor_stack:
                curr = possessor_stack.pop()
                for possessor in curr.possessors:
                    graph.add_node(possessor.id, possessor)
                    graph.add_edge(curr.id, possessor.id, "of")
                possessor_stack.extend(curr.possessors)

            for phrase_object in itertools.chain(phrase.agent_objects, phrase.patient_objects):
                for desc_by in phrase_object.described_by:
                    self._add_phrase(graph, desc_by, added_phrases, include_extensions)
                    for pred in desc_by.predicate:
                        graph.add_edge(phrase_object.id, pred.id, "described_by")

        for patient_phrase in phrase.patient_phrases:
            for my_pred, other_pred in itertools.product(phrase.predicate, patient_phrase.predicate):
                graph.add_edge(my_pred.id, other_pred.id, "patient")
            self._add_phrase(graph, patient_phrase, added_phrases, include_extensions)

        for agent_phrase in phrase.agent_phrases:
            for my_pred, other_pred in itertools.product(phrase.predicate, agent_phrase.predicate):
                graph.add_edge(my_pred.id, other_pred.id, "agent")
            self._add_phrase(graph, agent_phrase, added_phrases, include_extensions)

        for conditional_phrase in phrase.condition_phrases:
            for my_pred, other_pred in itertools.product(phrase.predicate, conditional_phrase.predicate):
                graph.add_edge(my_pred.id, other_pred.id, "conditional")
            self._add_phrase(graph, conditional_phrase, added_phrases, include_extensions)


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

    if not Doc.get_extension("document_structure"):
        # The root of this document.
        Doc.set_extension("document_structure", default=None)

    if not Doc.get_extension("reference_base"):
        # The root from where to resolve references.
        Doc.set_extension("reference_base", default=None)

    raw_text = ""
    # We keep a list of node content end positions in the text from which we derive which node each token
    # originates from
    text_positions: List[Tuple[int, Node]] = []

    for node in pre_order(analyzed):
        raw_text += node.content
        raw_text += "\n"
        text_positions.append((len(raw_text), node))

    # We create an anonymous pipe to insert infromation about the structure into the doc right after creation.
    comp_name = "document_supplement_component_" + str(uuid.uuid4())

    @Language.component(comp_name, assigns=["doc._.reference_base", "doc._.document_structure", "token._.node"])
    def comp(d):
        d._.document_structure = analyzed
        d._.reference_base = reference_base

        for tok in d:
            for pos, node in text_positions:
                if tok.idx < pos:
                    tok._.node = node
                    break
            else:
                logging.warning(f"Could not assign a node to token '{tok}'. This is most likely caused by a bug.")

        return d

    nlp.add_pipe(comp_name, first=True)

    return nlp(raw_text)


def create_graph(root: Node, analyzed: Node, fast: bool = False,
                 include_extensions: bool = False,
                 attribute_extractors: List[AttributeExtractor] = None,
                 entity_linker_supplier: Callable[[Doc], List[EntityLinker]] = None,
                 ) -> KnowledgeGraph:
    """
    Creates a knowledge graph from a parsed document.

    :param root: The document structure against which to resolve references.
    :param analyzed: The document structure from which to obtain the knowledge in the knowledge graph.
    :param fast: Determines if a faster spacy pipeline should be used.
    :param include_extensions: Determines if the 'of' and 'described_by' relationships should be added.
    :param attribute_extractors: A list of used attribute extractors. Defaults to negation and preposition extraction.
    :param entity_linker_supplier: A function for supplying entity linkers from a given Doc object.
    :return: The finished knowledge graph.
    """

    if attribute_extractors is None:
        attribute_extractors = [NegationExtractor(), PrepositionExtractor()]

    # We need to use coreferee so that PyCharm does not tidy up the import.
    if not coreferee:
        raise ModuleNotFoundError("Could not import coreferee for anaphora resolution.")

    if Token.get_extension("reference") is None:
        Token.set_extension("reference", default=None)

    if not Token.get_extension("node"):
        Token.set_extension("node", default=None)

    if fast:
        nlp = spacy.load("en_core_web_sm", disable=["ner"])
    else:
        nlp = spacy.load("en_core_web_trf", disable=["ner"])

    # We setup spaCy with all the necessary pipe components, both custom and from other libraries.
    # Resolves anaphoric references
    nlp.add_pipe("coreferee", config={}, after="parser")
    # Detects references
    nlp.add_pipe(RegexReferenceDetector.SPACY_COMPONENT_NAME, config={}, after="parser")
    # Creates reference qualifiers
    nlp.add_pipe(ReferenceResolver.SPACY_COMPONENT_NAME, config={},
                 after=RegexReferenceDetector.SPACY_COMPONENT_NAME)
    # Fully resolves references
    nlp.add_pipe(REFERENCE_QUALIFIER_RESOLVER_COMPONENT, config={},
                 after=ReferenceResolver.SPACY_COMPONENT_NAME)

    # Does some ugly setup of the Doc object and applies nlp
    doc = nlp_doc(root, analyzed, nlp)

    # Phrase Extraction
    phrases = []
    phrase_extractor = PhraseExtractor()
    for sent in doc.sents:
        phrases.extend(phrase_extractor.extract_from_sentence(sent))

    # Assembly
    graph = KGRenderer().render(root, phrases, include_extensions=include_extensions)

    # Attribute Extraction
    for attribute_extractor in attribute_extractors:
        graph = attribute_extractor.accept(graph)

    # Entity Linking
    entity_linkers = entity_linker_supplier(doc) if entity_linker_supplier is not None else [
        SameTokenLinker(),
        SameLemmaInSameParagraphLinker(doc),
        ReferenceLinker(doc),
        ProperNounLinker()
    ]

    with BatchedMerge(graph) as proxy_kg:
        for entity_linker in entity_linkers:
            entity_linker.link(proxy_kg)

    return graph
