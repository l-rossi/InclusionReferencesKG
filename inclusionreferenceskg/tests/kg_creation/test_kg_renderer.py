import spacy.util
from spacy.tokens import Token, Doc

from document_parsing.node.document import Document
from document_parsing.node.root import Root
from kg_creation.kg_renderer import KGRenderer
from kg_creation.sentence_analysing.phrase import Phrase, PhraseObject, Predicate
from reference import Reference


def test_kg_renderer_add_phrase_object_once():
    Token.set_extension("reference", default=None)

    doc = Doc(vocab=spacy.util.get_lang_class("en")().vocab, words=[f"t{i}" for i in range(3)])
    phrase_objects = [PhraseObject(tok) for tok in doc]

    p0 = Phrase()
    p0.patient_objects.append(phrase_objects[0])
    p0.patient_objects.append(phrase_objects[1])
    p0.agent_objects.append(phrase_objects[2])

    p1 = Phrase()
    p1.agent_objects.append(phrase_objects[0])
    p1.agent_objects.append(phrase_objects[1])
    p1.patient_objects.append(phrase_objects[2])

    renderer = KGRenderer()
    root = Root()
    graph = renderer.render(root=root, phrases=[p0, p1])

    assert set(graph.nodes.keys()) == {root.id, phrase_objects[0].id, phrase_objects[1].id, phrase_objects[2].id}


def test_kg_renderer_example():
    Token.set_extension("reference", default=None)
    Token.set_extension("node", default=None)

    doc = Doc(vocab=spacy.util.get_lang_class("en")().vocab, words=[f"t{i}" for i in range(13)])
    phrase_objects = [PhraseObject(tok) for tok in doc[:8]]
    predicates = [Predicate(tok) for tok in doc[8:]]

    document = Document()
    root = Root(children=[document])
    for tok in doc:
        tok._.node = document

    doc[7]._.reference = Reference(start=7, targets=[document], text_content=doc[7].text)

    p0 = Phrase()
    p0.predicate.append(predicates[0])
    p0.patient_objects.append(phrase_objects[0])
    p0.agent_objects.append(phrase_objects[1])

    p1 = Phrase()
    p1.predicate.append(predicates[1])
    p1.predicate.append(predicates[2])
    p1.agent_objects.append(phrase_objects[2])
    p1.patient_objects.append(phrase_objects[3])

    p2 = Phrase()
    p2.predicate.append(predicates[3])
    p2.agent_objects.append(phrase_objects[4])
    p2.patient_objects.append(phrase_objects[5])

    p3 = Phrase()
    p3.predicate.append(predicates[4])
    p3.agent_objects.append(phrase_objects[6])
    p3.patient_objects.append(phrase_objects[7])
    p3.agent_phrases.append(p0)
    p3.patient_phrases.append(p1)
    p3.condition_phrases.append(p2)

    renderer = KGRenderer()
    graph = renderer.render(root=root, phrases=[p3])

    assert len(graph.nodes) == 14

    assert predicates[0].id in graph.nodes.keys()
    assert set(graph.nodes[predicates[0].id].adj.keys()) == {phrase_objects[0].id, phrase_objects[1].id}
    assert graph.nodes[predicates[0].id].adj[phrase_objects[0].id][1] == "patient"
    assert graph.nodes[predicates[0].id].adj[phrase_objects[1].id][1] == "agent"
    assert graph.nodes[predicates[0].id].adj_in == {predicates[4].id}
    assert graph.nodes[phrase_objects[0].id].adj_in == {predicates[0].id}
    assert graph.nodes[phrase_objects[1].id].adj_in == {predicates[0].id}

    assert predicates[1].id in graph.nodes.keys()
    assert predicates[2].id in graph.nodes.keys()
    assert set(graph.nodes[predicates[1].id].adj.keys()) == {phrase_objects[2].id, phrase_objects[3].id}
    assert set(graph.nodes[predicates[2].id].adj.keys()) == {phrase_objects[2].id, phrase_objects[3].id}
    assert graph.nodes[predicates[1].id].adj[phrase_objects[3].id][1] == "patient"
    assert graph.nodes[predicates[2].id].adj[phrase_objects[3].id][1] == "patient"
    assert graph.nodes[predicates[1].id].adj[phrase_objects[2].id][1] == "agent"
    assert graph.nodes[predicates[2].id].adj[phrase_objects[2].id][1] == "agent"
    assert graph.nodes[predicates[1].id].adj_in == {predicates[4].id}
    assert graph.nodes[predicates[2].id].adj_in == {predicates[4].id}
    assert graph.nodes[phrase_objects[2].id].adj_in == {predicates[1].id, predicates[2].id}
    assert graph.nodes[phrase_objects[3].id].adj_in == {predicates[1].id, predicates[2].id}

    assert predicates[3].id in graph.nodes.keys()
    assert set(graph.nodes[predicates[3].id].adj.keys()) == {phrase_objects[4].id, phrase_objects[5].id}
    assert graph.nodes[predicates[3].id].adj[phrase_objects[4].id][1] == "agent"
    assert graph.nodes[predicates[3].id].adj[phrase_objects[5].id][1] == "patient"
    assert graph.nodes[predicates[3].id].adj_in == {predicates[4].id}
    assert graph.nodes[phrase_objects[4].id].adj_in == {predicates[3].id}
    assert graph.nodes[phrase_objects[5].id].adj_in == {predicates[3].id}

    assert predicates[4].id in graph.nodes.keys()
    assert set(graph.nodes[predicates[4].id].adj.keys()) == {predicates[0].id, predicates[1].id, predicates[2].id,
                                                             predicates[3].id, phrase_objects[6].id,
                                                             document.id}
    assert graph.nodes[predicates[4].id].adj[phrase_objects[6].id][1] == "agent"
    assert graph.nodes[predicates[4].id].adj[document.id][1] == "patient"
    assert graph.nodes[predicates[4].id].adj[predicates[0].id][1] == "agent"
    assert graph.nodes[predicates[4].id].adj[predicates[1].id][1] == "patient"
    assert graph.nodes[predicates[4].id].adj[predicates[2].id][1] == "patient"
    assert graph.nodes[predicates[4].id].adj[predicates[3].id][1] == "conditional"
    assert graph.nodes[predicates[4].id].adj_in == {document.id}
    assert graph.nodes[phrase_objects[6].id].adj_in == {predicates[4].id}
    assert graph.nodes[document.id].adj_in == {predicates[4].id, root.id}

    assert graph.nodes[root.id].adj[document.id][1] == "contains"
    assert set(graph.nodes[document.id].adj.keys()) == {predicates[4].id}
    assert graph.nodes[document.id].adj[predicates[4].id][1] == "defines"


def test_kg_renderer_recursion():
    Token.set_extension("reference", default=None)
    Token.set_extension("node", default=None)
    root = Root()

    doc = Doc(vocab=spacy.util.get_lang_class("en")().vocab, words=[f"t{i}" for i in range(3)])
    predicates = [Predicate(tok) for tok in doc]
    for tok in doc:
        tok._.node = root

    p0 = Phrase()
    p1 = Phrase()
    p2 = Phrase()

    p0.predicate.append(predicates[0])
    p1.predicate.append(predicates[1])
    p2.predicate.append(predicates[2])
    p0.agent_phrases.append(p1)
    p1.agent_phrases.append(p2)
    p2.agent_phrases.append(p0)

    renderer = KGRenderer()
    graph = renderer.render(root=root, phrases=[p0])

    assert set(graph.nodes.keys()) == {root.id, predicates[0].id, predicates[1].id, predicates[2].id}
    assert set(graph.nodes[predicates[0].id].adj.keys()) == {predicates[1].id}
    assert set(graph.nodes[predicates[1].id].adj.keys()) == {predicates[2].id}
    assert set(graph.nodes[predicates[2].id].adj.keys()) == {predicates[0].id}
