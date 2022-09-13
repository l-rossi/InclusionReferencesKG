from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.node_printer import print_nodes

if __name__ == "__main__":
    # document = DocumentTreeParser().parse_from_eu_doc_file("GDPR", "directive_2000_31_EC.txt")
    document = DocumentTreeParser().parse_from_eu_doc_file("GDPR", "gdpr.txt")
    print_nodes(document)
