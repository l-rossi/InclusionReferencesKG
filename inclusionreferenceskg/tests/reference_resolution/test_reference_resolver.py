from inclusionreferenceskg.src.document_parsing.node.article import Article
from inclusionreferenceskg.src.document_parsing.node.chapter import Chapter
from inclusionreferenceskg.src.document_parsing.node.document import Document
from inclusionreferenceskg.src.document_parsing.node.paragraph import Paragraph
from inclusionreferenceskg.src.document_parsing.node.point import Point
from inclusionreferenceskg.src.document_parsing.node.title import Title
from inclusionreferenceskg.src.reference import Reference
from inclusionreferenceskg.src.reference_resolution.reference_resolver import ReferenceResolver


def _references_eq_qualifiers(actual_references, expected_qualifiers):
    print(actual_references)

    assert len(actual_references) == 1
    assert len(actual_references[0].reference_qualifier) == len(expected_qualifiers)

    for actual_qualifier, expected_qualifier in zip(actual_references[0].reference_qualifier, expected_qualifiers):
        assert len(actual_qualifier) == len(expected_qualifier), "Got differing length of qualifier"
        for actual, expected in zip(actual_qualifier, expected_qualifier):
            assert actual.number == expected.number, "Got differing node numbering"
            assert actual.__class__ == expected.__class__, "Got differing node types"
            assert actual.title == expected.title, "Got differing node titles"


def test_point_after_paragraph():
    test_references = [Reference(0, "paragraph 2(b), (d) to (f), (h)")]
    expected_qualifiers = [
        [Article(number=1), Paragraph(number=2), Point(number=2)],
        [Article(number=1), Paragraph(number=2), Point(number=4)],
        [Article(number=1), Paragraph(number=2), Point(number=5)],
        [Article(number=1), Paragraph(number=2), Point(number=6)],
        [Article(number=1), Paragraph(number=2), Point(number=8)]
    ]

    resolver = ReferenceResolver()

    actual_references = resolver.resolve_single(Article(number=1), test_references)
    _references_eq_qualifiers(actual_references, expected_qualifiers)


def test_point_without_paragraph():
    test_references = [Reference(0, "Article 1(d)")]
    expected_qualifiers = [
        [Article(number=1), Point(number=4)]
    ]

    resolver = ReferenceResolver()

    actual_references = resolver.resolve_single(Chapter(number=1), test_references)
    _references_eq_qualifiers(actual_references, expected_qualifiers)


def test_paragraph_after_article():
    test_references = [Reference(0, "Article 1(2), (4) to (6), (8)")]
    expected_qualifiers = [
        [Article(number=1), Paragraph(number=2)],
        [Article(number=1), Paragraph(number=4)],
        [Article(number=1), Paragraph(number=5)],
        [Article(number=1), Paragraph(number=6)],
        [Article(number=1), Paragraph(number=8)]
    ]

    resolver = ReferenceResolver()

    actual_references = resolver.resolve_single(Article(number=2), test_references)
    _references_eq_qualifiers(actual_references, expected_qualifiers)


def test_multiple_directives_in_conjunction():
    test_references = [Reference(0, "Directives 95/46/EC and 97/66/EC")]
    expected_qualifiers = [
        [Document(title="Directive 95/46/EC")],
        [Document(title="Directive 97/66/EC")],
    ]

    resolver = ReferenceResolver()

    actual_references = resolver.resolve_single(Article(number=1), test_references)
    _references_eq_qualifiers(actual_references, expected_qualifiers)


def test_multiple_treaties():
    test_references = [Reference(0, "Titles V and VI of the Treaty on European Union")]
    expected_qualifiers = [
        [Document(title="the Treaty on European Union"), Title(number=5)],
        [Document(title="the Treaty on European Union"), Title(number=6)],
    ]

    resolver = ReferenceResolver()

    actual_references = resolver.resolve_single(Article(number=1), test_references)
    _references_eq_qualifiers(actual_references, expected_qualifiers)
