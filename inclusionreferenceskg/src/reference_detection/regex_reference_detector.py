import re
from typing import List

from spacy import Language

from inclusionreferenceskg.src.reference import Reference
from inclusionreferenceskg.src.reference_detection.reference_detector import ReferenceDetector
from inclusionreferenceskg.src.util.regex_util import RegexUtil


class RegexReferenceDetector(ReferenceDetector):
    """
    Reference detector based on regular expressions.
    """

    SPACY_COMPONENT_NAME = "reference_detector_component_regex"

    number_or_range = fr"(?:{RegexUtil.number}(?:\sto\s{RegexUtil.number})?)"
    para_or_range = fr"(?:{RegexUtil.para}(?:\sto\s{RegexUtil.para})?)"
    alph_or_range = fr"(?:{RegexUtil.alph}(?:\sto\s{RegexUtil.alph})?)"
    rom_or_range = fr"(?:{RegexUtil.rom}(?:\sto\s{RegexUtil.rom})?)"

    # https://publications.europa.eu/code/en/en-110202.htm
    document_numbering = r"(?:(?:\s\(\w{2,7}\))?(?:\sNo)?\s[1-9][0-9]*(?:\/[1-9][0-9]*)?(?:\/\w{2,7}))"
    document_numbering_plural = fr"(?:{document_numbering}(?:,{document_numbering})*(?:\s{RegexUtil.conj}{document_numbering})*)"

    regulation = fr"(?:(?:Commission\s)?Regulations?{document_numbering_plural})"
    directive = fr"(?:(?:(?:the\s{RegexUtil.ordinal}\s)?Council\s)?(?-i:Directive|Decision)s?{document_numbering_plural})"
    # treaty = r"(?:(?:the treaty (?:(?:[a-z]*){0,2} [A-Z][a-z]*)+)(?-i:\s\([A-Z]{2,}\))?|(?:the\s)?(?-i:[A-Z]{2,}))"
    treaty = r"(?:the\streaty\s(?:\w*\s)+(?-i:[A-Z]\w*)|the\s(?-i:[A-Z]{2,}))"

    document = fr"(?:(?:{regulation}|{directive}|{treaty})|(?:this\s|that\s)(?-i:Regulation|Treaty|Directive|Decision))"

    # Note, that node_name_rom may also be followed by a decimal number.
    node_name_dec = r"(?:article|paragraph|subparagraph|sentence|indent)"
    node_name_rom = r"(?:chapter|title|section)"
    node_name = fr"(?:{node_name_rom}|{node_name_dec})"

    thereof = r"(?:\sthereof)?"

    single = fr"(?:(?:article\s{RegexUtil.number}{RegexUtil.para}{thereof})|this\s{node_name}|the previous\s{node_name}|{node_name}\s{RegexUtil.number}{thereof}|{node_name_rom}\s{RegexUtil.rom}{thereof}|(?:the\s)?{RegexUtil.ordinal}\s{node_name}{thereof}|that\s{node_name}|{document})"
    multi = fr"(?:article\s{RegexUtil.number}{para_or_range}(?:, {para_or_range})*(?:\s{RegexUtil.conj}\s{para_or_range})*{thereof}|" \
            fr"{node_name_dec}\s{RegexUtil.number}{alph_or_range}(?:, {alph_or_range})*(?:\s{RegexUtil.conj}\s{alph_or_range})*{thereof}|" \
            fr"{node_name_dec}s?\s{number_or_range}(?:,\s{number_or_range})*(?:\s{RegexUtil.conj}\s{number_or_range})*{thereof}|" \
            fr"{node_name_rom}s?\s{rom_or_range}(?:,\s{rom_or_range})*(?:\s{RegexUtil.conj}\s{rom_or_range})*{thereof}|" \
            fr"those\s{node_name}s)"

    point = fr"(?:points?\s{alph_or_range}(?:(?:,\s{alph_or_range})*\s{RegexUtil.conj}\s{alph_or_range})*)"

    ref = fr"(?i)(?:(?:{point}(?:\sof\s{single})?)|(?:{multi}|{single}))(?:(?:\sof|,\s)?\s{single})*"

    def __init__(self):
        self.pattern: re.Pattern = RegexReferenceDetector._build_pattern()

    @staticmethod
    def _build_pattern() -> re.Pattern:
        return re.compile(RegexReferenceDetector.ref, re.I)

    def detect(self, text) -> List[Reference]:
        return [Reference(start=m.start(), text_content=m.group()) for m in self.pattern.finditer(text)]

    @staticmethod
    @Language.component(SPACY_COMPONENT_NAME, retokenizes=True, assigns=["token._.reference"])
    def as_spacy_pipe_component(doc):
        return ReferenceDetector._spacy_pipe_component_base(RegexReferenceDetector())(doc)

