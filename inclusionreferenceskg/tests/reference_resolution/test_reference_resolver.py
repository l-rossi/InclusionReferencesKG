from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.reference_resolution.reference_resolver import ReferenceResolver


def test_debug():
    resolver = ReferenceResolver()

    with open("./resources/gdpr.txt", "r") as gdpr_f:
        gdpr_t = gdpr_f.read()

    gdpr = DocumentTreeParser().parse_regulation("GDPR", gdpr_t)


    # TODO: make into an actual test
    resolver.resolve_all(gdpr)


