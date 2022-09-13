from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.node_printer import print_nodes


if __name__ == "__main__":

    with open("./resources/gdpr.txt", "r") as gdpr_file:
        gdpr_text = gdpr_file.read()

    parser = DocumentTreeParser()
    gdpr = parser.parse_document("GDPR", gdpr_text)
    print_nodes(gdpr)

    # print(PDFParser.parse_to_file("./resources/gdpr.pdf", "./resources/gdpr.txt"))
