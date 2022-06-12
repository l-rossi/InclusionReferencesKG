from typing import List

from inclusionreferenceskg.src.document_parsing.node.article import Article
from inclusionreferenceskg.src.document_parsing.node.chapter import Chapter
from inclusionreferenceskg.src.document_parsing.node.node import Node
from inclusionreferenceskg.src.document_parsing.node.node_traversal import pre_order
from inclusionreferenceskg.src.document_parsing.node.paragraph import Paragraph
from inclusionreferenceskg.src.document_parsing.node.point import Point
from inclusionreferenceskg.src.document_parsing.node.regulation import Regulation
from inclusionreferenceskg.src.document_parsing.node.subparagraph import Subparagraph
from inclusionreferenceskg.src.reference_detection.reference_detector import ReferenceDetector
from inclusionreferenceskg.src.reference_detection.regex_reference_detector import RegexReferenceDetector


class ReferenceResolver:
    """
    Class that takes the document structure as an input and uses a reference detector to resolve references.
    """

    def __init__(self, detector: ReferenceDetector = None, document_structure: List[Node] = None):
        if detector is None:
            detector = RegexReferenceDetector()
        self.detector = detector
        if document_structure is None:
            document_structure = [Regulation, Chapter, Article, Paragraph, Subparagraph, Point]
        self.document_structure = document_structure

    def resolve_all(self, node: Node):
        for curr in pre_order(node):
            self.resolve_single(curr)

    def resolve_single(self, node: Node):
        references = self.detector.detect(node.content)
