import itertools
import warnings
from typing import List, Dict, Tuple

import coreferee
import graphviz
import networkx as nx
import spacy
from spacy.tokens import Token

from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.article import Article
from inclusionreferenceskg.src.document_parsing.node.node import Node
from inclusionreferenceskg.src.document_parsing.node.node_traversal import pre_order
from inclusionreferenceskg.src.kg_creation.attribute_extraction.conditional_extractor import ConditionalExtractor
from inclusionreferenceskg.src.kg_creation.attribute_extraction.negation_extractor import NegationExtractor
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import Phrase
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase_extractor import PhraseExtractor
from inclusionreferenceskg.src.reference_detection.regex_reference_detector import RegexReferenceDetector
from inclusionreferenceskg.src.reference_resolution.reference_resolver import ReferenceResolver

"""
Translates the graph from the internal format to a format used by external libraries for analysing and visualisation.
"""


class KGRenderer:
    def render_to_networkx(self, root: Node, phrases: List[Phrase]) \
        -> (nx.Graph, Dict[str, str], Dict[Tuple[str, str], str], Dict[str, str]):
        """
        Returns the components for rendering a NetworkX Graph

        :param root:
        :param phrases:
        :return: The NetworkX Graph, node labels, edge labels, color labels
        """
        warnings.warn("KGRenderer.render_to_networkx is deprecated in favor of KGRenderer.render_to_graphviz.",
                      DeprecationWarning)

        graph = nx.DiGraph()
        node_labels: Dict[str, str] = {}
        edge_labels: Dict[Tuple[str, str], str] = {}
        node_colors: Dict[str, str] = {}

        # add document structure:
        for node in pre_order(root):
            graph.add_node(node.id)
            node_labels[node.id] = str(node.immutable_view())
            node_colors[node.id] = "purple"
            for child in node.children:
                graph.add_edge(node.id, child.id)
                edge_labels[(node.id, child.id)] = "contains"

        for phrase in phrases:
            self._add_phrase(graph, node_labels, edge_labels, node_colors, phrase)

        return graph, node_labels, edge_labels, node_colors

    def _add_phrase(self, graph: nx.Graph, node_labels: Dict[str, str], edge_labels: Dict[Tuple[str, str], str],
                    node_colors: Dict[str, str], phrase: Phrase):
        warnings.warn("KGRenderer._add_phrase is deprecated with KGRenderer.render_to_networkx.",
                      DeprecationWarning)

        for predicate in phrase.predicate:
            graph.add_node(predicate.id)
            node_labels[predicate.id] = str(predicate.token)

        if phrase.origin_node_id:
            for predicate in phrase.predicate:
                graph.add_edge(phrase.origin_node_id, predicate.id)
                edge_labels[(phrase.origin_node_id, predicate.id)] = "defines"

        for patient_object in phrase.patient_objects:
            if patient_object.token._.reference and (targets := patient_object.token._.reference.targets):
                for target, predicate in itertools.product(targets, phrase.predicate):
                    graph.add_edge(predicate.id, target.id)
                    edge_labels[(predicate.id, target.id)] = "patient"
            else:
                graph.add_node(patient_object.id)
                node_labels[patient_object.id] = str(patient_object.token)
                for predicate in phrase.predicate:
                    graph.add_edge(predicate.id, patient_object.id)
                    edge_labels[(predicate.id, patient_object.id)] = "patient"

        for agent_object in phrase.agent_objects:
            if agent_object.token._.reference and (targets := agent_object.token._.reference.targets):
                for target, predicate in itertools.product(targets, phrase.predicate):
                    graph.add_edge(predicate.id, target.id)
                    edge_labels[(predicate.id, target.id)] = "patient"
            else:
                graph.add_node(agent_object.id)
                node_labels[agent_object.id] = str(agent_object.token)
                for predicate in phrase.predicate:
                    graph.add_edge(predicate.id, agent_object.id)
                    edge_labels[(predicate.id, agent_object.id)] = "agent"

        for patient_phrase in phrase.patient_phrases:
            for my_pred, other_pred in itertools.product(phrase.predicate, patient_phrase.predicate):
                graph.add_edge(my_pred.id, other_pred.id)
                edge_labels[(my_pred.id, other_pred.id)] = "patient"
            self._add_phrase(graph, node_labels, edge_labels, node_colors, patient_phrase)

        for agent_phrase in phrase.agent_phrases:
            for my_pred, other_pred in itertools.product(phrase.predicate, agent_phrase.predicate):
                graph.add_edge(my_pred.id, other_pred.id)
                edge_labels[(my_pred.id, other_pred.id)] = "agent"
            self._add_phrase(graph, node_labels, edge_labels, node_colors, agent_phrase)

    def render_to_graphviz(self, root: Node, phrases: List[Phrase]):
        graph = graphviz.Digraph("GDPR", engine="dot", format="svg")
        # graph.graph_attr["ranksep"] = "20"
        graph.graph_attr["overlap"] = "true"

        # add document structure:
        for node in pre_order(root):
            graph.node(node.id, str(node.immutable_view()), color="purple")

            for child in node.children:
                graph.edge(tail_name=node.id, head_name=child.id, label="contains")

        for phrase in phrases:
            self._add_phrase_graphviz(graph, phrase)

        graph.render(directory='output/graphs', view=False)

    def _add_phrase_graphviz(self, graph, phrase):
        for predicate in phrase.predicate:
            graph.node(predicate.id, str(predicate.token))

        if phrase.origin_node_id:
            for predicate in phrase.predicate:
                graph.edge(phrase.origin_node_id, predicate.id, "defines")

        for patient_object in phrase.patient_objects:
            if patient_object.token._.reference and (targets := patient_object.token._.reference.targets):
                for target, predicate in itertools.product(targets, phrase.predicate):
                    graph.edge(predicate.id, target.id, "patient")
            else:
                graph.node(patient_object.id, str(patient_object.token))
                for predicate in phrase.predicate:
                    graph.edge(predicate.id, patient_object.id, "patient")

        for agent_object in phrase.agent_objects:
            if agent_object.token._.reference and (targets := agent_object.token._.reference.targets):
                for target, predicate in itertools.product(targets, phrase.predicate):
                    graph.edge(predicate.id, target.id, "agent")
            else:
                graph.node(agent_object.id, str(agent_object.token))
                for predicate in phrase.predicate:
                    graph.edge(predicate.id, agent_object.id, "agent")

        for patient_phrase in phrase.patient_phrases:
            for my_pred, other_pred in itertools.product(phrase.predicate, patient_phrase.predicate):
                graph.edge(my_pred.id, other_pred.id, "patient")
            self._add_phrase_graphviz(graph, patient_phrase)

        for agent_phrase in phrase.agent_phrases:
            for my_pred, other_pred in itertools.product(phrase.predicate, agent_phrase.predicate):
                graph.edge(my_pred.id, other_pred.id, "agent")
            self._add_phrase_graphviz(graph, agent_phrase)

        for conditional_phrase in phrase.condition_phrases:
            for my_pred, other_pred in itertools.product(phrase.predicate, conditional_phrase.predicate):
                graph.edge(my_pred.id, other_pred.id, "conditional")
            self._add_phrase_graphviz(graph, conditional_phrase)


def main():
    # We need to use coreferee so that PyCharm does not tidy up the reference.
    if not coreferee:
        print("Could not import coreferee for anaphora resolution.")

    spacy.prefer_gpu()

    gdpr = DocumentTreeParser().parse_from_eu_doc_file("GDPR", "gdpr.txt")
    article6 = gdpr.resolve_loose([Article(number=8)])[0]

    root = gdpr
    analyzed = article6

    attribute_extractors = [
        ConditionalExtractor(),
        NegationExtractor()
    ]

    Token.set_extension("reference", default=None)
    nlp = spacy.load("en_core_web_trf", disable=["ner"])
    nlp.add_pipe(RegexReferenceDetector.SPACY_COMPONENT_NAME, config={}, after="parser")
    nlp.add_pipe("coreferee", config={}, after="parser")

    phrase_extractor = PhraseExtractor()

    reference_resolver = ReferenceResolver()
    phrases = []

    content_nodes = ((node.content, node) for node in pre_order(analyzed) if node.content)
    for doc, node in nlp.pipe(content_nodes, as_tuples=True):
        references = [tok._.reference for tok in doc if tok._.reference]
        reference_resolver.resolve_single(node, references)

        for tok in doc:
            if tok._.reference:
                for qual in tok._.reference.reference_qualifier:
                    # We choose the first possible node
                    targets = root.resolve_loose(qual)
                    if len(targets) != 1:
                        warnings.warn(f"Got more than one possible target for reference {qual}")

                    if targets:
                        tok._.reference.targets.append(targets[0])

        for sent in doc.sents:
            phrases.extend(phrase_extractor.extract_from_sentence(sent, node=node))

    for phrase in phrases:
        for attribute_extractor in attribute_extractors:
            attribute_extractor.accept_with_children(phrase)

    """graph, node_labels, edge_labels, node_colors = KGRenderer().render_to_networkx(root=analyzed, phrases=phrases)

    pos = nx.drawing.nx_agraph.graphviz_layout(graph)
    nx.draw(graph, pos=pos, labels=node_labels, with_labels=True, node_color=node_colors)
    nx.draw_networkx_edge_labels(graph, pos=pos, edge_labels=edge_labels)"""

    KGRenderer().render_to_graphviz(analyzed, phrases)

    for phrase in phrases:
        phrase.pprint()

    # plt.show()


if __name__ == "__main__":
    main()
