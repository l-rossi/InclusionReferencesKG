import logging

import spacy

from document_parsing.document_tree_parser import DocumentTreeParser
from document_parsing.node.article import Article
from document_parsing.node.document import Document
from document_parsing.node.paragraph import Paragraph
from document_parsing.node.point import Point
from kg_creation.kg_renderer import create_graph
from util.parser_util import gdpr_dependency_root

if __name__ == "__main__":
    # This is the main entry point to the knowledge graph creation algorithm.

    # (setup logging)
    logging.basicConfig(level=logging.INFO)

    # We begin by choosing the documents we want to analyse:

    # A document must be read from a text file and parsed into the tree structure as described in the paper.
    # We begin by reading the file from disk. More documents can be added in ./inclusionreferenceskg/resources/.
    with open("./resources/eu_documents/gdpr.txt") as f:
        document_raw_text = f.read()

    # The PDFParser file provides some utility for parsing PDF documents. Note that some manual preprocessing, such
    # as the removal of unwanted preambles might be necessary:
    # PDFParser.parse_to_file("./resources/eu_documents/gdpr.pdf", "./resources/eu_documents/gdpr.txt")

    # We then instantiate a parser. One may configure the parser to only detect certain nodes
    # and change the used preprocessors:
    # node_patterns = [Article, Paragraph, Subparagraph]
    # preprocessors = [FootnoteDeletePreprocessor]
    # parser = DocumentTreeParser(node_patterns=node_patterns, preprocessors=preprocessors)

    # The default arguments for the parser are tuned to the GDPR.
    parser = DocumentTreeParser()

    # We can then parse the text to the target tree structure.
    _ = parser.parse_document(title="GDPR", text=document_raw_text)

    # Alternatively, we can use the parser to directly load a file in ./resources/eu_documents using:
    # gdpr = parser.parse_from_eu_doc_file(title="GDPR", file_name="gdpr.txt")

    # Instead we will use a utility function that provides us with the parsed GDPR, as well as a root node containing
    # the GDPR and all the documents referenced within.
    gdpr, document_root = gdpr_dependency_root()

    # We can select a specific document fragment by using Node.resolve_loose.
    # Note that the pattern attribute must be ordered by Node.depth in ascending order.
    # Node.resolve_lose returns a list of possible targets. We will choose the first entry of this list:
    gdpr_article30 = gdpr.resolve_loose(pattern=[Article(number=30)])[0]

    # Example of a more complex query:
    gdpr_article30_paragraph1_point5 = document_root.resolve_loose(pattern=
                                                                   [Document(title="GDPR"), Article(number=30),
                                                                    Paragraph(number=1), Point(number=5)])[0]

    # We must now do some configuration based on the current system.
    # spaCy may run either on the GPU or the CPU. We found a marginal speed increase on the GPU but the
    # amount of available VRAM might become critical.
    spacy.prefer_gpu()
    # spacy.require_cpu()

    # We may now create the knowledge graph by specifying two document fragments: the root, i.e., the document fragment
    # from which the document's structure should be built, and the analyzed document fragment, from which the
    # content of the knowledge graph should be derived.
    # One may for example want to only analyze the GDPR, whilst allowing references to other documents to
    # be captured properly.
    # The fast flag indicates whether spaCy should optimize for performance or for accuracy.
    # Attribute extractors and entity linkers may also be specified here, though the
    # default array is recommended.
    # The extensions, namely the 'of' relation and a 'described_by' relation for adnominal clauses can be added using
    # the 'include_extensions' flag.
    # The create_graph function is a good place for further examination of the codebase.
    graph = create_graph(root=gdpr_article30, analyzed=gdpr_article30, fast=True, attribute_extractors=None,
                         entity_linker_supplier=None, include_extensions=False)
    logging.info("The knowledge graph has been created. Now saving...")

    # The finished knowledge graph may then be exported into different formats, for example rendered
    # to a SVG file using graphviz. Note that this step is typically by far the most time intensive step for
    # large knowledge graphs. The visualized knowledge graph is stored in .\inclusionreferenceskg\output
    graph.as_graphviz_graph("Example_KG", engine="dot", format_="svg", attrs={"overlap": "true"}) \
        .render(directory='output/graphs', view=False)
    logging.info("The knowledge graph has been visualized and saved.")
