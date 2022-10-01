import re
from typing import List

from spacy import Language

from reference import Reference
from reference_detection.reference_detector import ReferenceDetector
from util.regex_util import RegexUtil


class RegexReferenceDetector(ReferenceDetector):
    """
    Reference detector based on regular expressions.
    """

    SPACY_COMPONENT_NAME = "reference_detector_component_regex"

    number_or_range = fr"(?:{RegexUtil.number}(?:\sto\s{RegexUtil.number})?)"
    paragraph_or_range = fr"(?:{RegexUtil.paragraph}(?:\sto\s{RegexUtil.paragraph})?)"
    alpha_or_range = fr"(?:{RegexUtil.alpha}(?:\sto\s{RegexUtil.alpha})?)"
    roman_or_range = fr"(?:{RegexUtil.roman}(?:\sto\s{RegexUtil.roman})?)"

    numbers = fr"(?:{number_or_range}(?:,\s{number_or_range})*(?:\s{RegexUtil.conjunction}\s{number_or_range})*)"
    paragraphs = fr"(?:{paragraph_or_range}(?:,\s{paragraph_or_range})*(?:\s{RegexUtil.conjunction}\s{paragraph_or_range})*)"
    alphas = fr"(?:{alpha_or_range}(?:,\s{alpha_or_range})*(?:\s{RegexUtil.conjunction}\s{alpha_or_range})*)"
    romans = fr"(?:{roman_or_range}(?:,\s{roman_or_range})*(?:\s{RegexUtil.conjunction}\s{roman_or_range})*)"

    thereof = r"(?:\sthereof)?"

    # https://publications.europa.eu/code/en/en-110202.htm
    document_numbering = r"(?:(?:\s\(\w{2,7}\))?(?:\sNo)?\s[1-9][0-9]*(?:\/[1-9][0-9]*)?(?:\/\w{2,7}))"
    document_numbering_plural = fr"(?:{document_numbering}(?:,{document_numbering})*(?:\s{RegexUtil.conjunction}{document_numbering})*)"

    regulation = fr"(?:(?:Commission\s)?Regulations?{document_numbering_plural})"
    directive = fr"(?:(?:(?:the\s{RegexUtil.ordinal}\s)?Council\s)?(?-i:Directive|Decision)s?{document_numbering_plural})"
    treaty = r"(?:the\streaty\s(?:\w*\s)+(?-i:[A-Z]\w*)|the\s(?-i:[A-Z]{2,}))"

    document = fr"(?:(?:{regulation}|{directive}|{treaty})|(?:this\s|that\s)(?-i:Regulation|Treaty|Directive|Decision))"

    # Note, that node_name_rom may also be followed by a decimal number.
    node_name_decimal = r"(?:article|paragraph|subparagraph|sentence|indent)"
    node_name_roman = r"(?:chapter|title|section)"
    node_name = fr"(?:{node_name_roman}|{node_name_decimal})"

    single = fr"(?:article\s{RegexUtil.number}{RegexUtil.paragraph}{thereof}|" \
             fr"(?:this|that|the\sprevious)\s{node_name}|" \
             fr"{node_name}\s{RegexUtil.number}{thereof}|" \
             fr"{node_name_roman}\s{RegexUtil.roman}{thereof}|" \
             fr"(?:the\s)?{RegexUtil.ordinal}\s{node_name}{thereof}|" \
             fr"{document}|" \
             fr"point\s{RegexUtil.alpha})"
    multi = fr"(?:article\s{RegexUtil.number}{paragraphs}{thereof}|" \
            fr"{node_name_decimal}\s{RegexUtil.number}{alphas}{thereof}|" \
            fr"{node_name_decimal}s?\s{numbers}{thereof}|" \
            fr"{node_name_roman}s?\s{romans}{thereof}|" \
            fr"those\s{node_name}s|" \
            fr"points?\s{alphas})"

    reference = fr"(?i)(?:{multi}|{single})(?:(?:\sof)?\s{single})*"

    def __init__(self):
        self.pattern: re.Pattern = RegexReferenceDetector._build_pattern()

    @staticmethod
    def _build_pattern() -> re.Pattern:
        return re.compile(RegexReferenceDetector.reference, re.I)

    def detect(self, text) -> List[Reference]:
        return [Reference(start=m.start(), text_content=m.group()) for m in self.pattern.finditer(text)]

    @staticmethod
    @Language.component(SPACY_COMPONENT_NAME, retokenizes=True, assigns=["token._.reference"])
    def as_spacy_pipe_component(doc):
        return ReferenceDetector._spacy_pipe_component_base(RegexReferenceDetector())(doc)
