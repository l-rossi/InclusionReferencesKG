from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.node_printer import NodePrinter

if __name__ == "__main__":
    parser = DocumentTreeParser()

    with open("./resources/eu_documents/teu.txt") as teu_file:
        teu = parser.parse_document("the TEU", teu_file.read())

    NodePrinter.print(teu)
