import pprint

from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.node_traversal import pre_order
from inclusionreferenceskg.src.document_parsing.preprocessing.footnote_delete_preprocessor import \
    FootnoteDeletePreprocessor
from inclusionreferenceskg.src.document_parsing.preprocessing.header_preprocessor import HeaderPreprocessor
from inclusionreferenceskg.src.reference_detection.reference_detector import ReferenceDetector
import csv
from difflib import SequenceMatcher, Differ

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

    d = Differ()
    print("\n".join(d.compare(detected_references, expected_references)))


def evaluate_regex_reference_detector_on_gdpr():
    """
    Calls evaluate_detector with the parameters for the gdpr and the RegexReferenceDetector.
    """
    # Extract the raw text from the GDPR (sans Titles)
    with open("./resources/eu_documents/gdpr.txt") as f:
        gdpr_text = f.read()

    parser = DocumentTreeParser(preprocessors=[HeaderPreprocessor, FootnoteDeletePreprocessor])
    gdpr = parser.parse_document("GDPR", gdpr_text)
    raw_text = "\n".join(node.content for node in pre_order(gdpr))

    evaluate_detector(RegexReferenceDetector(), raw_text, "./resources/evaluation_data/gdpr_references.csv")


if __name__ == "__main__":
    evaluate_regex_reference_detector_on_gdpr()
