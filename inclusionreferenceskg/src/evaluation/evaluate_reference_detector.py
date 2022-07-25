import csv
from difflib import Differ, SequenceMatcher

from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.node_traversal import pre_order
from inclusionreferenceskg.src.document_parsing.preprocessing.footnote_delete_preprocessor import \
    FootnoteDeletePreprocessor
from inclusionreferenceskg.src.document_parsing.preprocessing.header_preprocessor import HeaderPreprocessor
from inclusionreferenceskg.src.reference_detection.gold_standard_reference_detector import GoldStandardReferenceDetector
from inclusionreferenceskg.src.reference_detection.reference_detector import ReferenceDetector
from inclusionreferenceskg.src.reference_detection.regex_reference_detector import RegexReferenceDetector


def evaluate_detector(detector: ReferenceDetector, origin_text: str, expected_file: str):
    """
    Prints a diff of the references detected by the detector and those that are expected.

    :param detector: The tested detector.
    :param origin_text: The text to be searched for references.
    :param expected_file: The csv file containing the expected references.
    """

    detected_references = detector.detect(origin_text)

    with open(expected_file, "r", encoding="utf-8") as ef:
        expected_references = [x[0] for x in csv.reader(ef, delimiter=";")][1:]

    detected_references_text = [x.text_content for x in detected_references]
    d = Differ()
    print("  ---DIFF--")
    print("\n".join(d.compare(detected_references_text, expected_references)))

    sm = SequenceMatcher(None, detected_references_text, expected_references)

    false_positives = 0
    false_negatives = 0

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue

        false_positives += i2 - i1
        false_negatives += j2 - j1

    print("Number of false positives", false_positives)
    print("Number of false negatives", false_negatives)

    # TODO: Was tired when making this. Double-check
    true_positives = len(expected_references) - false_negatives

    precision = true_positives / len(detected_references)
    recall = true_positives / len(expected_references)
    f1 = 2 / (1 / recall + 1 / precision)

    print("Precision:", precision)
    print("Recall:", recall)
    print("F1:", f1)

    print("Ratio:", sm.ratio())


def evaluate_regex_reference_detector_on_gdpr():
    """
    Calls evaluate_detector with the parameters for the gdpr and the RegexReferenceDetector.

    Note: We evaluate against the GDPR without footnotes.
    """
    # Extract the raw text from the GDPR (sans Titles)
    with open("./resources/eu_documents/gdpr.txt") as f:
        gdpr_text = f.read()

    parser = DocumentTreeParser(preprocessors=[HeaderPreprocessor, FootnoteDeletePreprocessor])
    gdpr = parser.parse_document("GDPR", gdpr_text)
    raw_text = "\n".join(node.content for node in pre_order(gdpr))

    evaluate_detector(RegexReferenceDetector(), raw_text, "./resources/evaluation_data/gdpr_references.csv")


def evaluate_gold_standard_reference_detector_on_gdpr():
    """
    This is basically just a sanity check.

    Calls evaluate_detector with the parameters for the gdpr and the GoldStandardReferenceDetector.
    """
    # Extract the raw text from the GDPR (sans Titles)
    with open("./resources/eu_documents/gdpr.txt") as f:
        gdpr_text = f.read()

    parser = DocumentTreeParser(preprocessors=[HeaderPreprocessor, FootnoteDeletePreprocessor])
    gdpr = parser.parse_document("GDPR", gdpr_text)
    raw_text = "\n".join(node.content for node in pre_order(gdpr))
    evaluate_detector(GoldStandardReferenceDetector("./resources/evaluation_data/gdpr_references.csv"), raw_text,
                      "./resources/evaluation_data/gdpr_references.csv")


if __name__ == "__main__":
    with open("./resources/eu_documents/gdpr.txt") as f:
        gdpr_text = f.read()
    parser = DocumentTreeParser(preprocessors=[HeaderPreprocessor, FootnoteDeletePreprocessor])
    gdpr = parser.parse_document("GDPR", gdpr_text)
    raw_text = "\n".join(node.content for node in pre_order(gdpr))

    for x, y in zip(GoldStandardReferenceDetector().detect(raw_text), RegexReferenceDetector().detect(raw_text)):
        print(x, y)


    # evaluate_regex_reference_detector_on_gdpr()
    # evaluate_gold_standard_reference_detector_on_gdpr()
