from typing import Tuple

from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.document import Document
from inclusionreferenceskg.src.document_parsing.node.root import Root


def gdpr_dependency_root(parser: DocumentTreeParser = None) -> Tuple[Document, Root]:
    """
    Utility function for reading and parsing documents.

    :param parser: The parser to be used. If None, a default DocumentTreeParser is created.
    :return: A tuple of the document and the root node with the documents referred to in the GDPR.
    """

    docs = []
    parser = parser or DocumentTreeParser()

    gdpr = parser.parse_from_eu_doc_file("GDPR", "gdpr.txt")
    docs.append(gdpr)
    docs.append(parser.parse_from_eu_doc_file("TEU",
                                              "teu.txt"))
    docs.append(parser.parse_from_eu_doc_file("Directive 95/46/EC",
                                              "directive_95_46_ec.txt"))
    docs.append(parser.parse_from_eu_doc_file("Directive 2000/31/EC",
                                              "directive_2000_31_EC.txt"))
    docs.append(parser.parse_from_eu_doc_file("Directive (EU) 2015/1535",
                                              "directive_eu_2015_1535.txt"))
    docs.append(parser.parse_from_eu_doc_file("EN-ISO/IEC 17065/2012",
                                              "mock_en_iso_17065_2012.txt"))
    docs.append(parser.parse_from_eu_doc_file("Regulation (EC) No 45/2001",
                                              "regulation_ec_45_2001.txt"))
    docs.append(parser.parse_from_eu_doc_file("Regulation (EU) No 182/2011",
                                              "regulation_eu_182_2011.txt"))
    docs.append(parser.parse_from_eu_doc_file("Regulation (EC) No 765/2008",
                                              "regulation_ev_765_2008.txt"))
    docs.append(parser.parse_from_eu_doc_file("Directive 2002/58/EC",
                                              "directive_2002_58_ec.txt"))
    docs.append(parser.parse_from_eu_doc_file("Regulation (EC) No 1049/2001",
                                              "regulation_ec_1049_2001.txt"))
    docs.append(parser.parse_from_eu_doc_file("Regulation (EEC) No 339/93",
                                              "regulation_eec_339_93.txt"))

    document_root = Root(children=docs)
    for doc in document_root.children:
        doc.parent = document_root

    return gdpr, document_root
