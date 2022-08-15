import typing
from typing import List, Optional, Type

from spacy import Language
from spacy.tokens import Doc

from inclusionreferenceskg.src.document_parsing.node.article import Article
from inclusionreferenceskg.src.document_parsing.node.chapter import Chapter
from inclusionreferenceskg.src.document_parsing.node.document import Document
from inclusionreferenceskg.src.document_parsing.node.node import Node
from inclusionreferenceskg.src.document_parsing.node.node_traversal import pre_order
from inclusionreferenceskg.src.document_parsing.node.point import Point
from inclusionreferenceskg.src.document_parsing.node.section import Section
from inclusionreferenceskg.src.document_parsing.node.subparagraph import Paragraph
from inclusionreferenceskg.src.document_parsing.node.subparagraph import Subparagraph
from inclusionreferenceskg.src.document_parsing.node.title import Title
from inclusionreferenceskg.src.document_parsing.preprocessing.block_preprocessor import \
    BlockPreprocessor
from inclusionreferenceskg.src.document_parsing.preprocessing.footnote_append_preprocessor import \
    FootnoteAppendPreprocessor
from inclusionreferenceskg.src.document_parsing.preprocessing.header_preprocessor import \
    HeaderPreprocessor
from inclusionreferenceskg.src.document_parsing.preprocessing.initial_space_preprocessor import InitialSpacePreprocessor


class DocumentTreeParser:
    """
    Main class for parsing a EU regulation in text form to a tree on which operations can be easily made.
    """

    SPACY_COMPONENT_NAME = "document_tree_parser"

    def __init__(self, node_patterns=None, preprocessors: Optional[List[Type[BlockPreprocessor]]] = None):
        """
        Creates a DocumentTreeParser.

        :param node_patterns: The nodes that may be created in the tree. The order of this list is importance if any of
                              the used nodes use the Node.consumes flag.
        :param preprocessors: A list of preprocessors to first be applied to the raw text. This is order dependant.
        """
        if node_patterns is None:
            node_patterns = [Chapter, Title, Article, Paragraph, Section, Point, Subparagraph]
        self.node_patterns = node_patterns

        if preprocessors is None:
            preprocessors = [HeaderPreprocessor, InitialSpacePreprocessor, FootnoteAppendPreprocessor]
        self.preprocessors = preprocessors

    def parse_document(self, title: str, text: str) -> Document:
        """
        Creates a document tree from the source text of a regulation.

        :param title: The title of the regulation
        :param text: The source text.
        :return: The regulation root node of the parsed document.
        """

        regulation = Document(title=title)
        node_stack: typing.List[Node] = [regulation]

        blocks = DocumentTreeParser._blockize(text)
        for preprocessor in self.preprocessors:
            blocks = preprocessor.process(blocks)

        for block in blocks:
            for node_pattern in self.node_patterns:
                matched, new_node = node_pattern.accept_block(block, node_stack[-1])
                if matched:
                    # end all nodes with higher depth
                    while node_stack[-1].depth >= node_pattern.depth:
                        node_stack[-1].finalize()
                        node_stack.pop()

                    new_node.parent = node_stack[-1]
                    node_stack[-1].children.append(new_node)
                    node_stack.append(new_node)
                    if node_pattern.consumes:
                        break
            else:
                # Raw content
                node_stack[-1].content += "\n\n" + block

        for node in node_stack:
            node.finalize()

        return regulation

    def parse_from_eu_doc_file(self, name, file_name) -> Document:
        """
        Shorthand for opening a file in "./resources/eu_documents" and parsing it
        :param file_name: The filename of the document.
        :param name: The name of the regulation.
        :return: The Document node representing the document
        """
        with open(f"./resources/eu_documents/{file_name}", encoding="utf-8") as f:
            return self.parse_document(name, f.read())

    @staticmethod
    def _blockize(text) -> typing.List[str]:
        """
        Parses the input texts into a list of paragraphs.

        :param text: The text to be parsed.
        :return: A list of text blocks.
        """
        return [block.strip().replace("\n", " ").replace("­", "") for block in text.split("\n\n") if block.strip()]

    @staticmethod
    @Language.component(SPACY_COMPONENT_NAME, assigns=["doc.text"])
    def as_spacy_component(doc: Doc, title: str):
        Doc.set_extension("root", default=None)

        parser = DocumentTreeParser()
        root = parser.parse_document(title, doc.text)

        raw_text = ""
        # We keep a list of node content end positions in the text
        text_positions: List[Tuple[int, Node]] = []

        for node in pre_order(analyzed):
            raw_text += node.content
            raw_text += "\n"
            text_positions.append((len(raw_text), node))

        doc.text = raw_text
        doc._.root = root
        return doc
