import re

from inclusionreferenceskg.src.reference_detection.reference_detector import ReferenceDetector


class RegexReferenceDetector(ReferenceDetector):
    """
    Reference detector based on regular expressions.
    """
    number = r"(?:[1-9][0-9]*)"
    alph = r"(?:\([a-z]\))"
    para = fr"(?:\({number}\))"
    ordinal = "(?:first|second|third|fourth|fifth|sixth)"
    conj = fr"(?:and|or)"
    rom = r"(?:I?[XV]*I{0,3})"  # This is a really bad pattern and only matches the first few roman numerals and also alot of illegal ones.

    number_or_range = fr"(?:{number}(?:\sto\s{number})?)"
    para_or_range = fr"(?:{para}(?:\sto\s{para})?)"
    alph_or_range = fr"(?:{alph}(?:\sto\s{alph})?)"

    # https://publications.europa.eu/code/en/en-110202.htm
    document_numbering = r"(?:(?:\s\(\w{2,7}\))?(?:\sNo)?\s[1-9][0-9]*(?:\/[1-9][0-9]*)?(?:\/\w{2,7}))"
    # TODO: This does not work if the issuing entity is integrated into the quote.
    regulation = fr"(?:(?:Commission\s)?Regulation{document_numbering}?)"
    # TODO: See regulation
    directive = fr"(?:(?:(?:First\s)?Council\s)?Directive{document_numbering}?)"
    treaty = r"(?:(?:the treaty (?:(?:[a-z]*){0,2} [A-Z][a-z]*)+)(?-i:\s\([A-Z]{2,}\))?|(?:the\s)?(?-i:[A-Z]{2,}))"

    document = fr"(?:(?:this\s|that\s)?(?:{regulation}|{directive}|{treaty}))"

    # Note, that node_name_rom may also be followed by a decimal number for to the author unknown reason.
    node_name_dec = r"(?:article|paragraph|subparagraph)"
    node_name_rom = r"(?:chapter|title)"
    node_name = fr"(?:{node_name_rom}|{node_name_dec})"

    single = fr"(?:article\s{number}{para}|this\s{node_name}|the previous\s{node_name}|{node_name}\s{number}|{node_name_rom}\s{rom}|the\s{ordinal}\s{node_name}|that\s{node_name}|{document})"  # Missing thereof
    multi = fr"(?:{node_name}s?\s{number_or_range}(?:,\s{number_or_range})*(?:\s{conj}\s{number_or_range})*|article\s{number}{para_or_range}(?:, {para_or_range})*(?:\s{conj}\s{para_or_range})+)"

    point = fr"(?:points?\s{alph_or_range}(?:(?:,\s{alph_or_range})*\s{conj}\s{alph_or_range})*)"

    ref = fr"(?:{point}\sof\s{single})|(?:{single}|{multi})(?:(?:\sof)?\s{single})*"

    def __init__(self):
        self.pattern: re.Pattern = RegexReferenceDetector._build_pattern()

    @staticmethod
    def _build_pattern() -> re.Pattern:
        return re.compile(RegexReferenceDetector.ref, re.I)

    def detect(self, text):
        return self.pattern.findall(text)


if __name__ == "__main__":
    print(RegexReferenceDetector().pattern.pattern)
