import json
from typing import Dict

from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.node import Node
from inclusionreferenceskg.src.reference_detection.gold_standard_reference_detector import GoldStandardReferenceDetector
from inclusionreferenceskg.src.reference_resolution.reference_resolver import ReferenceResolver


def main():
    resolver = ReferenceResolver(
        detector=GoldStandardReferenceDetector("./resources/evaluation_data/gdpr_references.csv"))
    with open("./resources/eu_documents/gdpr.txt") as f:
        gdpr = DocumentTreeParser().parse_document("GDPR", f.read())

    actual_references = resolver.resolve_all(gdpr)
    # print(references)

    with open("./resources/evaluation_data/gdpr_resolved.json") as f:
        expected_references = json.load(f)

    for actual_reference, expected_reference in zip(actual_references, expected_references):
        if (l := len(actual_reference.reference_qualifier)) == 0:
            print(
                f"ReferenceResolver produced {l} reference qualifiers for reference '{actual_reference.text_content}'. Expected 1.")
            continue

        if "patterns" not in expected_reference:
            print(f"Skipping evaluation for '{expected_reference.get('text')}'. No patterns found.")
            continue

        resolved = []
        for reference_qualifier in actual_reference.reference_qualifier:
            resolved_single = gdpr.resolve_loose(reference_qualifier)
            if len(resolved_single) == 0:
                print(f"Could not resolve {actual_reference.text_content}")
                continue

            if len(resolved_single) > 1:
                print(
                    f"Found multiple solutions to reference '{actual_reference.text_content}'. Further testing is "
                    f"done only against the first resolved node.")
            resolved.append(resolved_single[0])

        if len(expected_reference["patterns"]) != len(resolved):
            print(
                f"Expected {len(expected_reference['patterns'])} solutions for "
                f"reference {actual_reference.text_content}. But found {len(resolved)}.")
            continue

        for pattern, solution in zip(expected_reference["patterns"], resolved):
            if not validate(solution, pattern):
                print(
                    f"Found solution for reference '{actual_reference}' was incorrect. "
                    f"'{resolved}' does not match '{pattern}'.")


def validate(node: Node, pattern: Dict) -> bool:
    """
    Validates that a node adheres to a pattern.
    :param node: The node to be tested.
    :param pattern: The pattern to test against
    """

    if pattern.get("title") and pattern["title"] != node.title:
        return False

    if pattern.get("number") and pattern["number"] != node.number:
        return False

    return True


if __name__ == "__main__":
    main()
