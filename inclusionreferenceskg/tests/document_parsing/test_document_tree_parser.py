from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.article import Article
from inclusionreferenceskg.src.document_parsing.node.chapter import Chapter
from inclusionreferenceskg.src.document_parsing.node.document import Document
from inclusionreferenceskg.src.document_parsing.node.paragraph import Paragraph
from inclusionreferenceskg.src.document_parsing.node.point import Point
from inclusionreferenceskg.src.document_parsing.node.section import Section
from inclusionreferenceskg.src.document_parsing.node.subparagraph import Subparagraph


def test_parse_regulation():
    text = """
CHAPTER II

Principles

Section 1

Fake Section Title

Article 5

Principles relating to processing of personal data

1. Personal data shall be:

(a)  processed lawfully, fairly and in a transparent manner in relation to the data subject (‘lawfulness, fairness and
transparency’);

(b)  collected for specified, explicit and legitimate purposes and not further processed in a manner that is incompatible
with those purposes; further processing for archiving purposes in the public interest, scientific or historical research
purposes or statistical purposes shall, in accordance with Article 89(1), not be considered to be incompatible with
the initial purposes (‘purpose limitation’);

(c)  adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed (‘data
minimisation’);

(d)  accurate and, where necessary, kept up to date; every reasonable step must be taken to ensure that personal data that
are inaccurate, having regard to the purposes for which they are processed, are erased or rectified without delay
(‘accuracy’);

4.5.2016 L 119/35 Official Journal of the European Union EN


(e)  kept in a form which permits identification of data subjects for no longer than is necessary for the purposes for
which the personal data are processed; personal data may be stored for longer periods insofar as the personal data
will be processed solely for archiving purposes in the public interest, scientific or historical research purposes or
statistical purposes in accordance with Article 89(1) subject to implementation of the appropriate technical and
organisational measures required by this Regulation in order to safeguard the rights and freedoms of the data subject
(‘storage limitation’);

(f)  processed in a manner that ensures appropriate security of the personal data, including protection against
unauthorised or unlawful processing and against accidental loss, destruction or damage, using appropriate technical
or organisational measures (‘integrity and confidentiality’).

2. The controller shall be responsible for, and be able to demonstrate compliance with, paragraph 1 (‘accountability’).

"""

    parser = DocumentTreeParser()
    actual = parser.parse_document("Test Regulation", text)

    expected = Document(title="Test Regulation", children=[
        Chapter(number=2, title="Principles", children=[
            Section(number=1, title="Fake Section Title", children=[
                Article(number=5, title="Principles relating to processing of personal data", children=[
                    Paragraph(number=1, children=[
                        Subparagraph(number=1, content="1. Personal data shall be:", children=[
                            Point(number=1, content="(a)  processed lawfully, fairly and in a transparent manner in "
                                                    "relation to the data subject (‘lawfulness, fairness and "
                                                    "transparency’);"),
                            Point(number=2,
                                  content="(b)  collected for specified, explicit and legitimate purposes and "
                                          "not further processed in a manner that is incompatible with those "
                                          "purposes; further processing for archiving purposes in the public "
                                          "interest, scientific or historical research purposes or statistical "
                                          "purposes shall, in accordance with Article 89(1), not be considered "
                                          "to be incompatible with the initial purposes (‘purpose "
                                          "limitation’);"),
                            Point(number=3,
                                  content="(c)  adequate, relevant and limited to what is necessary in relation "
                                          "to the purposes for which they are processed (‘data minimisation’);"),
                            Point(number=4, content="(d)  accurate and, where necessary, kept up to date; every "
                                                    "reasonable step must be taken to ensure that personal data that are "
                                                    "inaccurate, having regard to the purposes for which they are "
                                                    "processed, are erased or rectified without delay (‘accuracy’);"),
                            Point(number=5,
                                  content="(e)  kept in a form which permits identification of data subjects for no "
                                          "longer than is necessary for the purposes for which the personal data are "
                                          "processed; personal data may be stored for longer periods insofar as the "
                                          "personal data will be processed solely for archiving purposes in the public "
                                          "interest, scientific or historical research purposes or statistical purposes "
                                          "in accordance with Article 89(1) subject to implementation of the appropriate "
                                          "technical and organisational measures required by this Regulation in order to "
                                          "safeguard the rights and freedoms of the data subject (‘storage limitation’);"),
                            Point(number=6,
                                  content="(f)  processed in a manner that ensures appropriate security of the "
                                          "personal data, including protection against unauthorised or unlawful "
                                          "processing and against accidental loss, destruction or damage, "
                                          "using appropriate technical or organisational measures (‘integrity "
                                          "and confidentiality’)."),
                        ]),
                    ]),
                    Paragraph(number=2, children=[
                        Subparagraph(number=1, content="2. The controller shall be responsible for, and be able to "
                                                       "demonstrate compliance with, paragraph 1 (‘accountability’).")
                    ])
                ])
            ])
        ]),
    ])

    # fill parent positions
    node_stack = [expected]
    while node_stack:
        curr = node_stack.pop()
        for c in curr.children:
            c.parent = curr
        node_stack.extend(curr.children)

    # A simple == creates a recursion error so we will manually compare nodes.
    actual_stack = [actual]
    expected_stack = [expected]

    while actual_stack and expected_stack:
        assert len(actual_stack) == len(expected_stack)

        a, e = actual_stack.pop(0), expected_stack.pop(0)
        assert a.__class__ == e.__class__
        assert a.number == e.number
        assert a.title == e.title
        assert len(a.children) == len(e.children)

        actual_stack.extend(a.children)
        expected_stack.extend(e.children)
