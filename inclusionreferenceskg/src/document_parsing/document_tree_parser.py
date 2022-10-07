import typing
from typing import List, Optional, Type

from document_parsing.node.article import Article
from document_parsing.node.chapter import Chapter
from document_parsing.node.document import Document
from document_parsing.node.indent import Indent
from document_parsing.node.node import Node
from document_parsing.node.point import Point
from document_parsing.node.section import Section
from document_parsing.node.subparagraph import Paragraph
from document_parsing.node.subparagraph import Subparagraph
from document_parsing.node.title import Title
from document_parsing.preprocessing.block_preprocessor import \
    BlockPreprocessor
from document_parsing.preprocessing.footnote_append_preprocessor import \
    FootnoteAppendPreprocessor
from document_parsing.preprocessing.header_preprocessor import \
    HeaderPreprocessor
from document_parsing.preprocessing.initial_space_preprocessor import InitialSpacePreprocessor


class DocumentTreeParser:
    """
    Main class for parsing an EU regulation in text form to a tree on which operations can be easily made.
    """

    def __init__(self, node_patterns=None, preprocessors: Optional[List[Type[BlockPreprocessor]]] = None):
        """
        Creates a DocumentTreeParser.

        :param node_patterns: The nodes that may be created in the tree. The order of this list is importance if any of
                              the used nodes use the Node.consumes flag.
        :param preprocessors: A list of preprocessors to first be applied to the raw text. This is order dependant.
        """
        if node_patterns is None:
            node_patterns = [Chapter, Title, Article, Paragraph, Section, Point, Indent, Subparagraph]
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

    def parse_from_eu_doc_file(self, title, file_name) -> Document:
        """
        Shorthand for opening a file in "./resources/eu_documents" and parsing it
        :param file_name: The filename of the document.
        :param title: The name of the regulation.
        :return: The Document node representing the document
        """
        with open(f"./resources/eu_documents/{file_name}", encoding="utf-8") as f:
            return self.parse_document(title, f.read())

    @staticmethod
    def _blockize(text) -> typing.List[str]:
        """
        Parses the input texts into a list of paragraphs.

        :param text: The text to be parsed.
        :return: A list of text blocks.
        """
        return [block.strip().replace("\n", " ").replace("­", "") for block in text.split("\n\n") if block.strip()]
