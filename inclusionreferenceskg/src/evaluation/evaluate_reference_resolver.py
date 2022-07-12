import json
from typing import Dict, Tuple

from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.node import Node
from inclusionreferenceskg.src.document_parsing.node.root import Root
from inclusionreferenceskg.src.reference_detection.gold_standard_reference_detector import GoldStandardReferenceDetector
from inclusionreferenceskg.src.reference_resolution.reference_resolver import ReferenceResolver


def main():
    resolver = ReferenceResolver(
        detector=GoldStandardReferenceDetector("./resources/evaluation_data/gdpr_references.csv"))
    with open("./resources/eu_documents/gdpr.txt") as f:
        gdpr = DocumentTreeParser().parse_document("GDPR", f.read())

    with open("./resources/eu_documents/teu.txt") as f:
        teu = DocumentTreeParser().parse_document("TEU", f.read())

    actual_references = resolver.resolve_all(gdpr)
    # print(references)

    document_root = Root(children=[teu, gdpr])

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
            resolved_single = document_root.resolve_loose(reference_qualifier)
            if len(resolved_single) == 0:
                print(f"Could not resolve '{actual_reference.text_content}'")
                continue

            if len(resolved_single) > 1:
                print(
                    f"Found multiple solutions to reference '{actual_reference.text_content}'. Further testing is "
                    f"done only against the first resolved node.")
            resolved.append(resolved_single[0])

        if len(expected_reference["patterns"]) != len(resolved):
            print(
                f"Expected {len(expected_reference['patterns'])} solutions for "
                f"reference '{actual_reference.text_content}'. But found {len(resolved)}.")
            continue

        for pattern, solution in zip(expected_reference["patterns"], resolved):
            valid, msg = validate(solution, pattern)
            if not valid:
                print(
                    f"Found solution for reference '{actual_reference.text_content}' was incorrect.", msg)


def validate(node: Node, pattern: Dict) -> Tuple[bool, str]:
    """
    Validates that a node adheres to a pattern.
    :param node: The node to be tested.
    :param pattern: The pattern to test against
    """

    if pattern.get("title") and pattern["title"] != node.title:
        return False, f"Expected title '{pattern['title']}'. Got: '{node.title}'"

    if pattern.get("number") and pattern["number"] != node.number:
        print("Incorrect number")
        return False, f"Expected number '{pattern['number']}'. Got: '{node.number}'"

    if pattern.get("type") and pattern["type"].lower() != node.__class__.__name__.lower():
        return False, f"Expected type '{pattern['type']}'. Got: '{node.__class__.__name__}'"

    if pattern.get("starts_with") and not node.content.lower().startswith(pattern["starts_with"].lower()):
        return False, f"Expected the node to start with '{pattern['starts_with'][:10]}...'. Was: '{node.content[:10]}'."

    if pattern.get("has_child") and not any(validate(n, pattern["has_child"])[0] for n in node.children):
        return False, "Found no child matching pattern."

    return True, "Valid"


if __name__ == "__main__":
    main()
