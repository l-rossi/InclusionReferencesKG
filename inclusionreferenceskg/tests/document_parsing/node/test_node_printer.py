from document_parsing.node.article import Article
from document_parsing.node.chapter import Chapter
from document_parsing.node.document import Document
from document_parsing.node.node_printer import print_nodes
from document_parsing.node.paragraph import Paragraph
from document_parsing.node.point import Point


def test_print():
    out = []

    start_node = Document(title="Test Regulation", children=[
        Chapter(number=1, title="Test Chapter", children=[
            Article(number=1, title="Test Article", content="Art Cont", children=[
                Paragraph(number=1, content="Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam"),
                Paragraph(number=2, content="At vero eos et accusam et justo duo dolores et ea rebum."),
            ]),
            Article(number=2, title="Article Test", children=[
                Paragraph(number=1, content="Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam"),
                Paragraph(number=2, content="At vero eos et accusam et justo duo dolores et ea rebum.", children=[
                    Point(number=1, content="Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum"),
                    Point(number=2, content="Duis autem vel eum iriure dolor in hendrerit in vulputate"),
                ]),
            ]),
        ])
    ])

    expected = """Document None [Test Regulation]:
        Chapter 1 [Test Chapter]:
                Article 1 [Test Article]: Art Cont
                    Paragraph 1: Lorem ipsum dolor si...
                    Paragraph 2: At vero eos et accus...
                Article 2 [Article Test]:
                    Paragraph 1: Lorem ipsum dolor si...
                    Paragraph 2: At vero eos et accus...
                            Point 1: Stet clita kasd gube...
                            Point 2: Duis autem vel eum i..."""

    print_nodes(start_node, indent=4, output=lambda x: out.append(x))
    actual = "\n".join(out)

    assert expected == actual, "print_nodes did not print correctly."
