from document_parsing.node.article import Article
from document_parsing.node.chapter import Chapter
from document_parsing.node.document import Document
from document_parsing.node.paragraph import Paragraph
from document_parsing.node.point import Point
from document_parsing.node.subparagraph import Subparagraph


def _test_structure():
    return Document(title="Test Regulation", children=[
        Chapter(number=2, title="Principles", children=[
            Article(number=5, title="Principles relating to processing of personal data", children=[
                Paragraph(number=1, children=[
                    Subparagraph(number=1, content="1. Personal data shall be:", children=[
                        Point(number=1, content="(a)  processed lawfully, fairly and in a transparent manner in "
                                                "relation to the data subject (‘lawfulness, fairness and "
                                                "transparency’);"),
                        Point(number=2, content="(b)  collected for specified, explicit and legitimate purposes and "
                                                "not further processed in a manner that is incompatible with those "
                                                "purposes; further processing for archiving purposes in the public "
                                                "interest, scientific or historical research purposes or statistical "
                                                "purposes shall, in accordance with Article 89(1), not be considered "
                                                "to be incompatible with the initial purposes (‘purpose "
                                                "limitation’);"),
                        Point(number=3, content="(c)  adequate, relevant and limited to what is necessary in relation "
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
                        Point(number=6, content="(f)  processed in a manner that ensures appropriate security of the "
                                                "personal data, including protection against unauthorised or unlawful "
                                                "processing and against accidental loss, destruction or damage, "
                                                "using appropriate technical or organisational measures (‘integrity "
                                                "and confidentiality’)."),
                    ]),
                ]),
                Paragraph(number=2, children=[
                    Subparagraph(number=1,
                                 content="2. The controller shall be responsible for, and be able to demonstrate "
                                         "compliance with, paragraph 1 (‘accountability’).")
                ])
            ]),
            Article(number=6, title="Principles relating to processing of personal data", children=[
                Paragraph(number=1, children=[
                    Subparagraph(number=1, content="1. Personal data shall be:", children=[
                        Point(number=1, content="(a)  processed lawfully, fairly and in a transparent manner in "
                                                "relation to the data subject (‘lawfulness, fairness and "
                                                "transparency’);"),
                        Point(number=2, content="(b)  collected for specified, explicit and legitimate purposes and "
                                                "not further processed in a manner that is incompatible with those "
                                                "purposes; further processing for archiving purposes in the public "
                                                "interest, scientific or historical research purposes or statistical "
                                                "purposes shall, in accordance with Article 89(1), not be considered "
                                                "to be incompatible with the initial purposes (‘purpose "
                                                "limitation’);"),
                        Point(number=3, content="(c)  adequate, relevant and limited to what is necessary in relation "
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
                        Point(number=6, content="(f)  processed in a manner that ensures appropriate security of the "
                                                "personal data, including protection against unauthorised or unlawful "
                                                "processing and against accidental loss, destruction or damage, "
                                                "using appropriate technical or organisational measures (‘integrity "
                                                "and confidentiality’)."),
                    ]),
                ]),
                Paragraph(number=2, children=[
                    Subparagraph(number=1,
                                 content="2. The controller shall be responsible for, and be able to demonstrate "
                                         "compliance with, paragraph 1 (‘accountability’).")
                ])
            ])
        ]),
    ])


def test_resolve_loose():
    test_structure = _test_structure()

    query1 = [x for x in test_structure.resolve_loose([Article(number=-1)])]
    assert len(query1) == 2
    assert query1[0].__class__ == Article and query1[0].number == 5 and query1[1].__class__ == Article and query1[
        1].number == 6

    query2 = [x for x in test_structure.resolve_loose([Article(number=5), Point(number=5)])]
    assert len(query2) == 1
    assert query2[0].__class__ == Point and query2[0].number == 5

    query3 = [x for x in test_structure.resolve_loose([Article(number=5), Point(number=7)])]
    assert len(query3) == 0
