import spacy.util
from spacy.tokens import Doc

from kg_creation.attribute_extraction.negation_extractor import NegationExtractor
from kg_creation.attribute_extraction.preposition_extractor import PrepositionExtractor
from kg_creation.knowledge_graph import KnowledgeGraph, KGNode
from kg_creation.sentence_analysing.phrase import Predicate, PhraseObject


def test_negation_extractor():
    # No, this sentence makes no sense...
    doc = Doc(vocab=spacy.util.get_lang_class("en")().vocab, words=[
        "I", "do", "not", "believe", "in", "fate", "unless", "I", "am",
        "not", "convinced", "otherwise", "."
    ])

    doc[0].head, doc[0].pos_, doc[0].dep_ = doc[3], "PRON", "nsubj"
    doc[1].head, doc[1].pos_, doc[1].dep_ = doc[3], "AUX", "aux"
    doc[2].head, doc[2].pos_, doc[2].dep_ = doc[3], "PART", "neg"
    doc[3].head, doc[3].pos_, doc[3].dep_ = doc[3], "VERB", "ROOT"
    doc[4].head, doc[4].pos_, doc[4].dep_ = doc[3], "ADP", "prep"
    doc[5].head, doc[5].pos_, doc[5].dep_ = doc[4], "NOUN", "pobj"
    doc[6].head, doc[6].pos_, doc[6].dep_ = doc[10], "SCONJ", "mark"
    doc[7].head, doc[7].pos_, doc[7].dep_ = doc[10], "PRON", "nsubjpass"
    doc[8].head, doc[8].pos_, doc[8].dep_ = doc[10], "AUX", "auxpass"
    doc[9].head, doc[9].pos_, doc[9].dep_ = doc[10], "PART", "neg"
    doc[10].head, doc[10].pos_, doc[10].dep_ = doc[3], "VERB", "advcl"
    doc[11].head, doc[11].pos_, doc[11].dep_ = doc[10], "ADV", "advmod"
    doc[12].head, doc[12].pos_, doc[12].dep_ = doc[3], "PUNCT", "punct"

    graph = KnowledgeGraph()
    graph.add_node("believe_node", Predicate(id="1", token=doc[3]))
    graph.add_node("convinced_node", Predicate(id="2", token=doc[10]))

    extractor = NegationExtractor()
    extractor.accept(graph)

    assert "negated" in graph.nodes.get("believe_node").attributes
    assert "negated" in graph.nodes.get("convinced_node").attributes
    assert graph.nodes.get("believe_node").attributes.get("negated")
    assert not graph.nodes.get("convinced_node").attributes.get("negated")


def test_preposition_extractor():
    doc = Doc(vocab=spacy.util.get_lang_class("en")().vocab, words=[
        "I", "want", "to", "be", "in", "bed", "right", "now", "."
    ])

    doc[0].head, doc[0].pos_, doc[0].dep_ = doc[1], "PRON", "nsubj"
    doc[1].head, doc[1].pos_, doc[1].dep_ = doc[1], "VERB", "ROOT"
    doc[2].head, doc[2].pos_, doc[2].dep_ = doc[3], "PART", "aux"
    doc[3].head, doc[3].pos_, doc[3].dep_ = doc[1], "AUX", "xcomp"
    doc[4].head, doc[4].pos_, doc[4].dep_ = doc[3], "ADP", "prep"
    doc[5].head, doc[5].pos_, doc[5].dep_ = doc[4], "NOUN", "pobj"
    doc[6].head, doc[6].pos_, doc[6].dep_ = doc[7], "ADV", "advmod"
    doc[7].head, doc[7].pos_, doc[7].dep_ = doc[3], "ADV", "advmod"
    doc[8].head, doc[8].pos_, doc[8].dep_ = doc[1], "PUNCT", "punct"

    graph = KnowledgeGraph()
    graph.add_node("I", PhraseObject(id="1", token=doc[0]))
    graph.add_node("want", Predicate(id="3", token=doc[1]))
    graph.add_node("be", Predicate(id="4", token=doc[3]))
    graph.add_node("bed", PhraseObject(id="2", token=doc[5]))
    graph.add_edge("want", "I", "agent")
    graph.add_edge("want", "be", "patient")
    graph.add_edge("be", "bed", "patient")

    extractor = PrepositionExtractor()
    extractor.accept(graph)

    assert "prepositions" in graph.nodes.get("be").adj.get("bed")[2]
    preps = graph.nodes.get("be").adj.get("bed")[2].get("prepositions")
    assert len(preps) == 1
    assert preps[0].text == "in"

    for node in graph.nodes.values():
        if node.id == "be":
            continue

        assert all(("prepositions" not in x[2]) for x in node.adj.values())
