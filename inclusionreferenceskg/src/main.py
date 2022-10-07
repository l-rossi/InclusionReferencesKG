import spacy

from document_parsing.document_tree_parser import DocumentTreeParser
from document_parsing.node.article import Article
from document_parsing.node.chapter import Chapter
from document_parsing.node.document import Document
from document_parsing.node.paragraph import Paragraph
from document_parsing.node.point import Point
from document_parsing.node.section import Section
from document_parsing.node.subparagraph import Subparagraph
from document_parsing.node.title import Title
from document_parsing.preprocessing.footnote_delete_preprocessor import FootnoteDeletePreprocessor
from kg_creation.kg_renderer import create_graph
from util.parser_util import gdpr_dependency_root

if __name__ == "__main__":
    # This is the main entry point to the knowledge graph creation algorithm.

    # We begin by choosing the documents we want to analyse:

    # A document must be read from a text file and parsed into the tree structure as described in the paper.
    # We begin by reading the file from disk
    with open("./resources/eu_documents/gdpr.txt") as f:
        document_raw_text = f.read()

    # We then instantiate a parser. One may configure the parser to only detect certain nodes
    # and only change the used preprocessors:
    # node_patterns = [Article, Paragraph, Subparagraph]
    # preprocessors = [FootnoteDeletePreprocessor]
    # parser = DocumentTreeParser(node_patterns=node_patterns, preprocessors=preprocessors)

    # The default arguments for the parser a tuned to the GDPR
    parser = DocumentTreeParser()

    # We can then parse the text to the target tree structure.
    _ = parser.parse_document(title="GDPR", text=document_raw_text)

    # Alternatively, we can use the parser to directly load a file in ./resources/eu_ducoments using:
    # gdpr = parser.parse_from_eu_doc_file(title="GDPR", file_name="gdpr.txt")

    # Instead we will use a utility function that provides us with the parsed GDPR, as well as a root node containing
    # the GDPR and all the documents referenced within.
    gdpr, document_root = gdpr_dependency_root()

    # We can select a specific document fragment by using Node.resolve_loose.
    # Note that the pattern attribute must be ordered by Node.id in descending order.
    # Node.resolve_lose returns a list of possible targets. We will choose the first entry of this list:
    gdpr_article30 = gdpr.resolve_loose(pattern=[Article(number=30)])[0]

    # Example of a more complex query:
    gdpr_article30_paragraph1_point5 = document_root.resolve_loose(pattern=
                                                                   [Document(title="GDPR"), Article(number=30),
                                                                    Paragraph(number=1), Point(number=5)])[0]

    # We must now do some configuration based on the current system.
    # spaCy may run either on the GPU or the CPU. We found a marginal speed increase on the GPU but the
    # amount of available VRAM might become critical.
    # Trying create a graph from the entire document_root when optimizing for accuracy was not
    # possible on a GPU with 11GB of VRAM but posed no problem when using the CPU and regular RAM (32GB):
    spacy.prefer_gpu()
    # spacy.require_cpu()

    # We may now create the knowledge graph specifying two document fragments: the root, i.e., the document fragment
    # from which the document's structure should be built, and the analyzed document fragment, from which the
    # content of the knowledge graph should be derived.
    # One may for example want to only analyze the GDPR, whilst allowing references to other documents to
    # be captured properly.
    # The fast flag indicates whether spaCy should optimize for performance or for accuracy.
    # Attribute extractors and entity linkers may also be specified here, though the
    # default array is recommended.
    # The extensions, namely the 'of' relation and a 'described_by' relation for adnominal clauses can be added using
    # the 'include_extensions' flag.
    graph = create_graph(root=gdpr_article30, analyzed=gdpr_article30, fast=False, attribute_extractors=None,
                         entity_linker_supplier=None, include_extensions=False)

    print("The knowledge graph has been created.")

    # The finished knowledge graph may then be exported into different formats, for example rendered
    # to a SVG file using graphviz. Note that this step is typically by far the most time intensive step for
    # large knowledge graphs.
    graph.as_graphviz_graph("Example_KG", engine="dot", format_="svg", attrs={"overlap": "true"}) \
        .render(directory='output/graphs', view=False)
