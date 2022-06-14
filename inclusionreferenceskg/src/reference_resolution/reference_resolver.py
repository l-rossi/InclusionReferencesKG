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
from inclusionreferenceskg.src.util.util import rom_to_dec


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
        patterns = []
        for reference in references:
            split_references = reference.split(" of ")


            for split_reference in split_references:
                pattern_for_split = []
                pattern_for_split.extend(self._extract_basic_references(split_reference, Article, RegexReferenceDetector.number))
                pattern_for_split.extend(self._extract_basic_references(split_reference, Paragraph, RegexReferenceDetector.number))
                pattern_for_split.extend(self._extract_basic_references(split_reference, Point, RegexReferenceDetector.alph))
                pattern_for_split.extend(self._extract_basic_references(split_reference, Chapter, RegexReferenceDetector.rom))
                pattern_for_split.extend(self._extract_basic_references(split_reference, Chapter, RegexReferenceDetector.number))

                # TODO this references with search for match in path to root in current node
                # TODO that references with search for previous match

                patterns.append(pattern_for_split)

            # TODO split patterns into multiple patterns so that each pattern only contains one node of a certain type:
            # [Paragraph(1), Paragraph(2), Article(3)] -> [], [Paragraph(2), Article(3)], [Paragraph(1), Article(3)]

            for pattern in patterns:
                pattern.sort(key=lambda x: x.depth)

            print(reference, ":", patterns)

        return patterns

    def _extract_basic_references(self, text, node_type, number_format):
        """

        :param prefix:
        :param number_format: Use one of RegexReferenceDetector.number,
                                         RegexReferenceDetector.alph,
                                         RegexReferenceDetector.para,
                                         RegexReferenceDetector.rom
        :return:
        """

        if number_format not in [RegexReferenceDetector.number, RegexReferenceDetector.alph,
                                 RegexReferenceDetector.para, RegexReferenceDetector.rom]:
            raise ValueError(f"number_format must be in [RegexReferenceDetector.number, RegexReferenceDetector.alph,"
                             f" RegexReferenceDetector.para, RegexReferenceDetector.rom], was: {number_format}")

        number_or_range_pattern = fr"({number_format}(?:\sto\s{number_format})?)"
        range_pattern = fr"({number_format}) to ({number_format})"

        main_pattern = fr"{node_type.__name__}s?\s({number_or_range_pattern}(?:,\s{number_or_range_pattern})*(?:\s(?:{RegexReferenceDetector.conj})\s{number_or_range_pattern})*)"

        new_nodes_for_pattern = []
        main_match = re.match(main_pattern, text, re.I)
        if not main_match:
            return []

        for number_or_range in main_match.groups()[1:]:
            if number_or_range is None:
                continue

            range_match = re.match(range_pattern, number_or_range, re.I)
            if range_match:
                for i in range(self._translate_number(number_format, range_match[1]),
                               self._translate_number(number_format, range_match[2]) + 1):
                    new_nodes_for_pattern.append(node_type(number=i))
                continue

            number_match = re.match(fr"({RegexReferenceDetector.number})", number_or_range, re.I)
            if number_match:
                new_nodes_for_pattern.append(
                    node_type(number=self._translate_number(number_format, number_match[1])))
                continue

        return new_nodes_for_pattern


    @staticmethod
    def _translate_number(number_format, number):
        """
        :param number_format: Use one of RegexReferenceDetector.number,
                                         RegexReferenceDetector.alph,
                                         RegexReferenceDetector.para,
                                         RegexReferenceDetector.rom
        :return:
        """

        if number_format not in [RegexReferenceDetector.number, RegexReferenceDetector.alph,
                                 RegexReferenceDetector.para, RegexReferenceDetector.rom]:
            raise ValueError(f"number_format must be in [RegexReferenceDetector.number, RegexReferenceDetector.alph,"
                             f" RegexReferenceDetector.para, RegexReferenceDetector.rom], was: {number_format}")

        if number_format == RegexReferenceDetector.number:
            return int(number)
        elif number_format == RegexReferenceDetector.alph:
            return ord(number[1:-1])
        elif number_format == RegexReferenceDetector.para:
            return int(number[1:-1])
        elif number_format == RegexReferenceDetector.rom:
            return rom_to_dec(number)
        return None
