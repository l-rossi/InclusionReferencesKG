from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.reference_resolution.reference_resolver import ReferenceResolver


def test_debug():
    resolver = ReferenceResolver()

    with open("./resources/eu_documents/gdpr.txt", "r") as gdpr_f:
        gdpr_t = gdpr_f.read()

    gdpr = DocumentTreeParser().parse_document("GDPR", gdpr_t)

    # TODO: make into an actual test
    # resolver.resolve_all(gdpr)

    references = resolver.resolve_all(gdpr)
    for reference in references:
        print(reference.text_content)
        for i, single_qualifier in enumerate(reference.reference_qualifier):
            print(f"Qualifier {i}:")
            print(single_qualifier)
            resolved = gdpr.resolve_loose(single_qualifier)
            if not resolved:
                print("Could not resolve")

            if len(resolved) > 2:
                print("Qualifier ambiguous:")

            for resolved_single in resolved:
                print(type(resolved_single), resolved_single.title, resolved_single.number)

        print("-" * 10)
