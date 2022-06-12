from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.article import Article
from inclusionreferenceskg.src.document_parsing.node.node_printer import NodePrinter
from inclusionreferenceskg.src.document_parsing.node.node_traversal import pre_order
from inclusionreferenceskg.src.reference_resolution.reference_resolver import ReferenceResolver


def test_debug():
    resolver = ReferenceResolver()

    with open("./resources/gdpr.txt", "r") as gdpr_f:
        gdpr_t = gdpr_f.read()

    gdpr = DocumentTreeParser().parse_regulation("GDPR", gdpr_t)

    article27 = gdpr.resolve([None, None, None, Article(number=27)])[0]

    # TODO: make into an actual test

    for a in pre_order(article27):
        NodePrinter.print(a)
        resolver.resolve_single(a)
        print("--------")

