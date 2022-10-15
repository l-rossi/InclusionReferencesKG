import uuid

import spacy.util
from spacy.tokens import Doc, Token

from document_parsing.node.article import Article
from document_parsing.node.document import Document
from document_parsing.node.node_traversal import pre_order
from document_parsing.node.paragraph import Paragraph
from document_parsing.node.subparagraph import Subparagraph
from kg_creation.entity_linking.proper_noun_linker import ProperNounLinker
from kg_creation.entity_linking.reference_linker import ReferenceLinker
from kg_creation.entity_linking.same_lemma_in_same_paragraph_linker import SameLemmaInSameParagraphLinker
from kg_creation.knowledge_graph import KnowledgeGraph
from kg_creation.sentence_analysing.phrase import PhraseObject
from util.reference import Reference


def test_reference_linker():
    if Doc.get_extension("coref_chains"):
        # We need to remove the coref chains if multiple tests are run in the same runtime.
        Doc.remove_extension("coref_chains")

    if not Token.get_extension("node"):
        Token.set_extension("node", default=None)

    if not Token.get_extension("reference"):
        Token.set_extension("reference", default=None)

    if not Doc.get_extension("document_structure"):
        Doc.set_extension("document_structure", default=None)

    if not Doc.get_extension("reference_base"):
        Doc.set_extension("reference_base", default=None)

    text1 = ["I", "diligently", "write", "tests"]
    text2 = ["The", "tests", "referred", "to", "in", "paragraph 1", "are", "important"]

    document = Document(title="Document", children=[
        Article(number=1, children=[
            Paragraph(number=1, children=[
                Subparagraph(number=1)
            ])
        ]),
        Article(number=2, children=[
            Paragraph(number=1, children=[
                Subparagraph(number=1)
            ])])
    ])

    for node in pre_order(document):
        for child in node.children:
            child.parent = node

    vocab = spacy.util.get_lang_class("en")().vocab
    doc = Doc(vocab, words=text1 + text2)

    doc[6].pos_ = "VERB"
    doc[7].pos_ = "ADP"
    doc[8].pos_ = "ADP"
    doc[9].pos_ = "PROPN"
    doc[9].tag_ = "REF"
    doc[9]._.reference = Reference(start=9, targets=[document.children[0].children[0]], text_content="paragraph 1")

    for tok in doc[:len(text1)]:
        tok._.node = document.children[0].children[0].children[0]

    for tok in doc[len(text1):]:
        tok._.node = document.children[1].children[0].children[0]

    graph = KnowledgeGraph()

    id_1 = str(uuid.uuid4())
    id_2 = str(uuid.uuid4())
    graph.add_node(id_1, PhraseObject(doc[3]))
    graph.add_node(id_2, PhraseObject(doc[5]))

    doc._.document_structure = document
    doc._.reference_base = document

    linker = ReferenceLinker(doc)

    closure_dict = {"merged": False}

    def mock_merge(u, v):
        if (u, v) == (id_1, id_2) or (u, v) == (id_2, id_1):
            closure_dict["merged"] = True
        else:
            assert False, "Merged incorrect nodes"

    graph.merge = mock_merge
    linker.link(graph)

    assert closure_dict["merged"], "Did not merge nodes"


def test_lemma_linker():
    if not Token.get_extension("node"):
        Token.set_extension("node", default=None)

    if not Token.get_extension("reference"):
        Token.set_extension("reference", default=None)

    if not Doc.get_extension("document_structure"):
        Doc.set_extension("document_structure", default=None)

    if not Doc.get_extension("reference_base"):
        Doc.set_extension("reference_base", default=None)

    text1 = ["Tests", "are", "great", ".", "I", "love", "this", "test", "."]
    text2 = ["These", "are", "not", "the", "tests", "you", "are", "looking", "for", "."]

    document = Document(title="Document", children=[
        Article(number=1, children=[
            Paragraph(number=1, children=[
                Subparagraph(number=1)
            ])
        ]),
        Article(number=2, children=[
            Paragraph(number=1, children=[
                Subparagraph(number=1)
            ])])
    ])

    for node in pre_order(document):
        for child in node.children:
            child.parent = node

    vocab = spacy.util.get_lang_class("en")().vocab
    doc = Doc(vocab, words=text1 + text2)

    doc[0].pos_ = "NOUN"
    doc[0].lemma_ = "test"
    doc[7].pos_ = "NOUN"
    doc[7].lemma_ = "test"
    doc[13].pos_ = "NOUN"
    doc[13].lemma_ = "test"

    for tok in doc[:len(text1)]:
        tok._.node = document.children[0].children[0].children[0]

    for tok in doc[len(text1):]:
        tok._.node = document.children[1].children[0].children[0]

    graph = KnowledgeGraph()

    id_1 = str(uuid.uuid4())
    id_2 = str(uuid.uuid4())
    id_3 = str(uuid.uuid4())
    graph.add_node(id_1, PhraseObject(doc[0]))
    graph.add_node(id_2, PhraseObject(doc[7]))
    graph.add_node(id_3, PhraseObject(doc[13]))

    doc._.document_structure = document
    doc._.reference_base = document

    linker = SameLemmaInSameParagraphLinker(doc)

    closure_dict = {"merged": False}

    def mock_merge(u, v):
        if (u, v) == (id_1, id_2) or (u, v) == (id_2, id_1):
            closure_dict["merged"] = True
        else:
            assert False, "Merged incorrect nodes"

    graph.merge = mock_merge
    linker.link(graph)

    assert closure_dict["merged"], "Did not merge nodes"


def test_proper_noun_linker():
    if not Token.get_extension("node"):
        Token.set_extension("node", default=None)

    if not Token.get_extension("reference"):
        Token.set_extension("reference", default=None)

    if not Doc.get_extension("document_structure"):
        Doc.set_extension("document_structure", default=None)

    if not Doc.get_extension("reference_base"):
        Doc.set_extension("reference_base", default=None)

    text1 = ["The", "EU", "'s", "Member", "States", "are", "great", "."]
    text2 = ["I", "like", "the", "Member", "States", "."]
    text3 = ["The", "United", "States", "are", "a", "country", "."]

    document = Document(title="Document", children=[
        Article(number=1, children=[
            Paragraph(number=1, children=[
                Subparagraph(number=1)
            ])
        ]),
        Article(number=2, children=[
            Paragraph(number=1, children=[
                Subparagraph(number=1)
            ])])
    ])

    for node in pre_order(document):
        for child in node.children:
            child.parent = node

    vocab = spacy.util.get_lang_class("en")().vocab
    doc = Doc(vocab, words=text1 + text2 + text3)

    doc[3].dep_ = "compound"
    doc[3].pos_ = "PROPN"
    doc[3].head = doc[4]
    doc[4].pos_ = "PROPN"
    doc[11].dep_ = "compound"
    doc[11].pos_ = "PROPN"
    doc[11].head = doc[12]
    doc[12].pos_ = "PROPN"
    doc[15].dep_ = "compound"
    doc[15].pos_ = "PROPN"
    doc[15].head = doc[16]
    doc[16].pos_ = "PROPN"

    for tok in doc[:len(text1)]:
        tok._.node = document.children[0].children[0].children[0]

    for tok in doc[len(text1):len(text1) + len(text2)]:
        tok._.node = document.children[1].children[0].children[0]

    graph = KnowledgeGraph()

    id_1 = str(uuid.uuid4())
    id_2 = str(uuid.uuid4())
    id_3 = str(uuid.uuid4())
    graph.add_node(id_1, PhraseObject(doc[4]))
    graph.add_node(id_2, PhraseObject(doc[12]))
    graph.add_node(id_3, PhraseObject(doc[16]))

    doc._.document_structure = document
    doc._.reference_base = document

    linker = ProperNounLinker()

    closure_dict = {"merged": False}

    def mock_merge(u, v):
        if (u, v) == (id_1, id_2) or (u, v) == (id_2, id_1):
            closure_dict["merged"] = True
        else:
            assert False, "Merged incorrect nodes"

    graph.merge = mock_merge
    linker.link(graph)

    assert closure_dict["merged"], "Did not merge nodes"
