import itertools
import re
import typing
import warnings
from typing import List, Type

from collections import defaultdict

from inclusionreferenceskg.src.document_parsing.node.article import Article
from inclusionreferenceskg.src.document_parsing.node.chapter import Chapter
from inclusionreferenceskg.src.document_parsing.node.document import Document
from inclusionreferenceskg.src.document_parsing.node.node import Node
from inclusionreferenceskg.src.document_parsing.node.node_traversal import pre_order
from inclusionreferenceskg.src.document_parsing.node.paragraph import Paragraph
from inclusionreferenceskg.src.document_parsing.node.point import Point
from inclusionreferenceskg.src.document_parsing.node.subparagraph import Subparagraph
from inclusionreferenceskg.src.document_parsing.node.title import Title
from inclusionreferenceskg.src.reference import Reference
from inclusionreferenceskg.src.reference_detection.reference_detector import ReferenceDetector
from inclusionreferenceskg.src.reference_detection.regex_reference_detector import RegexReferenceDetector
from inclusionreferenceskg.src.util.regex_util import RegexUtil
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
            document_structure = [Document, Chapter, Article, Paragraph, Subparagraph, Point]
        self.document_structure = document_structure

    def resolve_all(self, node: Node) -> List[Reference]:
        """
        Resolves this node and its children.
        :param node:
        :return:
        """

        references = []
        for curr in pre_order(node):
            references.extend(self.resolve_single(curr))
        return references

    def resolve_single(self, node: Node) -> List[Reference]:
        """
        Resolves the references in this node.

        :param node: The node for which the references should be resolved.
        :return: None
        """
        references = self.detector.detect(node.content)

        patterns = []
        for reference in references:
            if reference.reference_qualifier:
                warnings.warn("Overriding exiting reference qualifier for reference.")
                reference.reference_qualifier = []

            split_references = reference.text_content.split(" of ")

            components_of_reference = []
            for split_reference in split_references:
                pattern_for_split = []
                pattern_for_split.extend(
                    self._extract_basic_references(split_reference, Article, RegexUtil.number))
                pattern_for_split.extend(
                    self._extract_basic_references(split_reference, Paragraph, RegexUtil.number))
                pattern_for_split.extend(
                    self._extract_basic_references(split_reference, Point, RegexUtil.alph))
                pattern_for_split.extend(
                    self._extract_basic_references(split_reference, Chapter, RegexUtil.rom))
                pattern_for_split.extend(
                    self._extract_basic_references(split_reference, Title, RegexUtil.rom))
                pattern_for_split.extend(
                    self._extract_basic_references(split_reference, Chapter, RegexUtil.number))
                pattern_for_split.extend(self._resolve_ordinal(split_reference))

                pattern_for_split.extend(self._resolve_this(split_reference, node))
                pattern_for_split.extend(self._resolve_that(split_reference, patterns))
                pattern_for_split.extend(self._resolve_those(split_reference, patterns))
                pattern_for_split.extend(self._resolve_document(split_reference))
                pattern_for_split.extend(self._resolve_paragraph_after_article(split_reference))

                # Thereof requires the current split_reference to be at least partially parsed.
                pattern_for_split.extend(self._resolve_thereof(split_reference, patterns, pattern_for_split))

                # TODO add items to components_of_reference directly?
                if pattern_for_split:
                    components_of_reference.extend(pattern_for_split)
                else:
                    print(f"Could not detect any component from split_string: '{split_reference}'")
                    # TODO this implies an unparsed split and should be handeld
                    pass

            # split patterns into multiple patterns so that each pattern only contains one node of a certain type:
            # [Paragraph(1), Paragraph(2), Article(3)] -> [], [Paragraph(2), Article(3)], [Paragraph(1), Article(3)]
            grouped_nodes = defaultdict(list)
            for pattern_component in components_of_reference:
                grouped_nodes[pattern_component.__class__].append(pattern_component)

            patterns_translated = [list(x) for x in itertools.product(*grouped_nodes.values()) if x]

            # Fully qualify the reference by using the path from the root to this Node as a specifier
            for resolved in patterns_translated:
                highest_specified_node = min(resolved, key=lambda x: x.depth)

                c = node
                while c is not None and c.depth >= highest_specified_node.depth:
                    c = c.parent

                specifier = []
                while c is not None:
                    if not c.ignore_when_forming_full_qualifier:
                        specifier.append(self._node_to_node_pattern(c))
                    c = c.parent
                resolved.extend(specifier)
                resolved.sort(key=lambda x: x.depth)

            reference.reference_qualifier = patterns_translated
            patterns.extend(patterns_translated)
        return references

    @staticmethod
    def _resolve_paragraph_after_article(text: str) -> List[Node]:
        """
        Resolves paragraphs that occur after the definition of an article, i.e., Article ?? (1), (2) and (3)

        :param text: The part of the reference to scan for a match.
        :return: A list of nodes corresponding to those in the reference.
        """

        number_format = RegexUtil.para

        number_or_range_pattern = fr"({number_format}(?:\sto\s{number_format})?)"
        main_pattern = fr"article\s{RegexUtil.number}{number_or_range_pattern}(?:,\s{number_or_range_pattern})*(?:\s(?:{RegexUtil.conj})\s{number_or_range_pattern})*"

        return ReferenceResolver._extract_from_pattern(text, main_pattern, number_format, Paragraph)

    @staticmethod
    def _extract_basic_references(text: str, node_type: Type[Node], number_format: str) -> List[Node]:
        """
        Extracts references that start by a mention of the type of node and are followed by numbers.

        Note to viewers using PyCharm: PyCharm for some reason does not recognise a valid constructor for Type[Node]
        with parameters. This seems to be an error of PyCharm.

        :param number_format: Use one of RegexReferenceDetector.number, \
                                         RegexReferenceDetector.alph, \
                                         RegexReferenceDetector.para, \
                                         RegexReferenceDetector.rom
        :return: A list of nodes corresponding to those in the reference. This is used as a pattern\
        to compare against the document structure
        """

        if number_format not in [RegexUtil.number, RegexUtil.alph,
                                 RegexUtil.para, RegexUtil.rom]:
            raise ValueError(f"number_format must be in [RegexReferenceDetector.number, RegexReferenceDetector.alph,"
                             f" RegexReferenceDetector.para, RegexReferenceDetector.rom], was: {number_format}")

        number_or_range_pattern = fr"({number_format}(?:\sto\s{number_format})?)"
        main_pattern = fr"{node_type.__name__}s?\s{number_or_range_pattern}(?:,\s{number_or_range_pattern})*(?:\s(?:{RegexUtil.conj})\s{number_or_range_pattern})*"

        return ReferenceResolver._extract_from_pattern(text, main_pattern, number_format, node_type)

    @staticmethod
    def _extract_from_pattern(text: str, main_pattern: str, number_format: str, node_type: Type[Node]) -> List[Node]:
        """
        Extracts nodes based on a regex pattern.

        :param text: The text of the reference.
        :param main_pattern: The pattern to detect the reference.
        :param number_format: The number format used in conjunction with the node type.
        :param node_type: The type of node that should be created.
        :return: A list of detected references.
        """
        range_pattern = fr"({number_format}) to ({number_format})"
        new_nodes_for_pattern = []
        main_match = re.match(main_pattern, text, re.I)

        if not main_match:
            return []

        for number_or_range in main_match.groups():
            if number_or_range is None:
                continue

            range_match = re.match(range_pattern, number_or_range, re.I)
            if range_match:
                for i in range(ReferenceResolver._translate_number(number_format, range_match[1]),
                               ReferenceResolver._translate_number(number_format, range_match[2]) + 1):
                    new_nodes_for_pattern.append(ReferenceResolver._pattern_from_node(node_type, number=i))
                continue

            number_match = re.match(fr"({number_format})", number_or_range, re.I)
            if number_match:
                new_nodes_for_pattern.append(
                    ReferenceResolver._pattern_from_node(node_type,
                                                         number=ReferenceResolver._translate_number(number_format,
                                                                                                    number_match[1])))
                continue

        return new_nodes_for_pattern

    @staticmethod
    def _resolve_document(text) -> List[Node]:
        """
        Resolves references to documents. Names are not normalized.
        """

        # We do not use RegexReferenceDetector.document as it also matches too much

        regulation = fr"(?:Commission\s)?Regulation{RegexReferenceDetector.document_numbering}"
        directive = fr"(?:(?:First\s)?Council\s)?Directive{RegexReferenceDetector.document_numbering}"
        treaty = r"(?:the treaty (?:(?:[a-z]*){0,2} [A-Z][a-z]*)+)(?-i:\s\([A-Z]{2,}\))?|(?:the\s)?(?-i:[A-Z]{2,})"
        pattern = fr"{regulation}|{directive}|{treaty}"

        if re.match(pattern, text, re.I):
            return [ReferenceResolver._pattern_from_node(Document, title=text)]
        return []

    @staticmethod
    def _resolve_this(text: str, current_node: Node) -> List[Node]:
        """
        Resolves references introduced by 'this'.
        """

        def _resolve_name_to_node(name: str, node_type: Type[Node]):
            pattern = fr"this\s{name}"
            if not re.match(pattern, text, re.I):
                return []

            path_to_root = []
            record_path = False
            c = current_node
            while c is not None:
                if c.__class__ == node_type:
                    record_path = True
                if record_path:
                    path_to_root.append(
                        ReferenceResolver._pattern_from_node(c.__class__, number=c.number, title=c.title))
                c = c.parent
            return path_to_root

        for nt in Node.__subclasses__():
            if ret := _resolve_name_to_node(nt.__name__, nt):
                return ret

        for document_name in ["regulation", "directive", "treaty"]:
            if ret := _resolve_name_to_node(document_name, Document):
                return ret

        return []

    @staticmethod
    def _resolve_that(text: str, previous_references: List[List[Node]]) -> List[Node]:
        """
        Resolves references introduced by 'that'.
        """

        def _resolve_name_to_node(name: str, node_type: Type[Node]):
            pattern = fr"that\s{name}"
            if not re.match(pattern, text, re.I):
                return []

            for prev_ref in reversed(previous_references):
                pref_ref_sorted = sorted(prev_ref, key=lambda x: x.depth, reverse=True)
                for i, pref_ref_node in enumerate(pref_ref_sorted):
                    if pref_ref_node.__class__ == node_type:
                        return pref_ref_sorted[i:]

        for nt in Node.__subclasses__():
            if ret := _resolve_name_to_node(nt.__name__, nt):
                return ret

        for document_name in ["regulation", "directive", "treaty"]:
            if ret := _resolve_name_to_node(document_name, Document):
                return ret

        return []

    @staticmethod
    def _resolve_those(text: str, previous_references: List[List[Node]]) -> List[Node]:
        """
        Resolves references introduced by 'those'.

        WARNING: This method assumes that all nodes have the same path to the root. This assumption holds for the GDPR
        but is not guaranteed to hold in other documents.
        """

        def _resolve_name_to_node(name: str, node_type: Type[Node]):
            pattern = fr"those\s{name}s"
            if not re.match(pattern, text, re.I):
                return []

            ret = []

            for prev_ref in reversed(previous_references):
                pref_ref_sorted = sorted(prev_ref, key=lambda x: x.depth, reverse=True)
                for i, pref_ref_node in enumerate(pref_ref_sorted):
                    if pref_ref_node.__class__ == node_type:
                        # The path from the root to the detected node is only added for the first detected node.
                        # Subsequent nodes are assumed to have the same path to the root. This is not ideal behaviour.
                        if ret:
                            ret.append(pref_ref_sorted[i])
                        else:
                            ret.extend(pref_ref_sorted[i:])
            return ret

        for nt in Node.__subclasses__():
            if ret := _resolve_name_to_node(nt.__name__, nt):
                return ret

        return []

    @staticmethod
    def _resolve_ordinal(text: str) -> List[Node]:
        """
        Resolves nodes introduced by ordinals.
        :param text: The text content of the reference.
        :return:
        """
        ordinal_map = {
            "first": 1,
            "second": 2,
            "third": 3,
            "fourth": 4,
            "fifth": 5,
            "sixth": 6,
        }

        for node_type in Node.__subclasses__():
            pattern = fr"the\s({'|'.join(str(x) for x in ordinal_map.keys())})\s{node_type.__name__}"
            match = re.match(pattern, text, re.I)
            if match:
                return [ReferenceResolver._pattern_from_node(node_type, number=ordinal_map[match[1]])]

        return []

    @staticmethod
    def _resolve_thereof(text: str,
                         previous_references: List[List[Node]],
                         current_parsed_reference: List[Node]) -> List[Node]:
        """
        Resolves references ending in thereof.

        :param text: The text content of the reference.
        :param previous_references: Previously resolved references.
        :param current_parsed_reference: The current state of the \
        reference being parsed, i.e., the part before the 'thereof'.
        :return: The qualifier represented by the 'thereof'.
        """

        if text.lower().endswith("thereof"):
            if not previous_references:
                print(f"Found use of thereof for text '{text}' although no previous references are present.")
                return []

            if not current_parsed_reference:
                print(f"Found use of thereof for text '{text}' with no node specifier."
                      f"Thereof requires the reference to be at least partially qualified.")
                return []

            last_reference = previous_references[-1]
            # We will resolve thereof by finding the node with the largest depth whose depth is smaller than the
            # parsed node's depth.
            min_depth_part_of_current_reference = min(current_parsed_reference, key=lambda x: x.depth)
            return list(filter(lambda x: x.depth < min_depth_part_of_current_reference.depth, last_reference))

        return []

    @staticmethod
    def _pattern_from_node(node_type: Type[Node], number: int = None, title: str = None) -> Node:
        """
        Utility method for creating nodes. Necessary as subclasses of Node may overwrite the __init__ method of
        the Node base class.

        :param node_type: The type of node to be created.
        :param number: The number of the new node.
        :param title: The title of the new node.
        :return: An instance of the node_type.
        """
        new_node = node_type()
        new_node.number = number
        new_node.title = title
        return new_node

    @staticmethod
    def _node_to_node_pattern(node: Node) -> Node:
        new_node = node.__class__()
        new_node.number = node.number
        new_node.title = node.title
        return new_node

    @staticmethod
    def _translate_number(number_format, number):
        """
        :param number_format: Use one of RegexReferenceDetector.number,\
                                         RegexReferenceDetector.alph,\
                                         RegexReferenceDetector.para,\
                                         RegexReferenceDetector.rom
        :return:
        """

        if number_format not in [RegexUtil.number, RegexUtil.alph,
                                 RegexUtil.para, RegexUtil.rom]:
            raise ValueError(f"number_format must be in [RegexReferenceDetector.number, RegexReferenceDetector.alph,"
                             f" RegexReferenceDetector.para, RegexReferenceDetector.rom], was: {number_format}")

        if number_format == RegexUtil.number:
            return int(number)
        elif number_format == RegexUtil.alph:
            return ord(number[1:-1]) - 96
        elif number_format == RegexUtil.para:
            return int(number[1:-1])
        elif number_format == RegexUtil.rom:
            return rom_to_dec(number)
        return None
