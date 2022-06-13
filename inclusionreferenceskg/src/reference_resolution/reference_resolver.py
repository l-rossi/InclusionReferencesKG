import itertools
import re
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
            print("-" * 10)
            print(curr.content)
            self.resolve_single(curr)
            print("-" * 10)

    def resolve_single(self, node: Node):
        references = self.detector.detect(node.content)

        print(references)
        for reference in references:
            split_references = reference.split(" of ")

            patterns = [[]]

            for split_reference in split_references:
                article_match = re.match(
                    fr"articles?\s({RegexReferenceDetector.number_or_range})(?:,\s({RegexReferenceDetector.number_or_range}))*(?:\s({RegexReferenceDetector.conj})\s({RegexReferenceDetector.number_or_range}))*",
                    split_reference, re.I)
                if article_match:
                    range_pattern = fr"({RegexReferenceDetector.number}) to ({RegexReferenceDetector.number})"
                    new_articles = []
                    for number_or_range in article_match.groups():
                        if number_or_range is None:
                            continue

                        range_match = re.match(range_pattern, number_or_range, re.I)
                        if range_match:
                            for i in range(int(range_match[1]), int(range_match[2]) + 1):
                                new_articles.append(Article(number=i))
                            continue

                        number_match = re.match(fr"({RegexReferenceDetector.number})", number_or_range, re.I)
                        if number_match:
                            new_articles.append(Article(number=int(number_match[1])))
                            continue

                    # For each referenced article, we must construct one fully qualified pattern.
                    new_patterns = []
                    for new_article, old_pattern in itertools.product(new_articles, patterns):
                        new_patterns.append(old_pattern + [new_article])
                    patterns = new_patterns

            for pattern in patterns:
                pattern.sort(key=lambda x: x.depth)

            print(reference, ":", patterns)
            return patterns
