import json
from typing import Dict, Tuple

from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.node import Node
from inclusionreferenceskg.src.document_parsing.node.node_traversal import pre_order
from inclusionreferenceskg.src.document_parsing.node.root import Root
from inclusionreferenceskg.src.reference_detection.gold_standard_reference_detector import GoldStandardReferenceDetector
from inclusionreferenceskg.src.reference_resolution.reference_resolver import ReferenceResolver


def main():
    resolver = ReferenceResolver()

    parser = DocumentTreeParser()
    reference_detector = GoldStandardReferenceDetector("./resources/evaluation_data/gdpr_references.csv")

    docs = []

    with open("./resources/eu_documents/gdpr.txt", encoding="utf-8") as f:
        gdpr = parser.parse_document("GDPR", f.read())
        docs.append(gdpr)

    with open("./resources/eu_documents/teu.txt", encoding="utf-8") as f:
        docs.append(parser.parse_document("TEU", f.read()))

    with open("./resources/eu_documents/directive_95_46_ec.txt", encoding="utf-8") as f:
        docs.append(parser.parse_document("Directive 95/46/EC", f.read()))

    with open("./resources/eu_documents/directive_2000_31_EC.txt", encoding="utf-8") as f:
        docs.append(parser.parse_document("Directive 2000/31/EC", f.read()))

    with open("./resources/eu_documents/directive_eu_2015_1535.txt", encoding="utf-8") as f:
        docs.append(parser.parse_document("Directive (EU) 2015/1535", f.read()))

    with open("./resources/eu_documents/mock_en_iso_17065_2012.txt", encoding="utf-8") as f:
        docs.append(parser.parse_document("EN-ISO/IEC 17065/2012", f.read()))

    with open("./resources/eu_documents/regulation_ec_45_2001.txt", encoding="utf-8") as f:
        docs.append(parser.parse_document("Regulation (EC) No 45/2001", f.read()))

    with open("./resources/eu_documents/regulation_eu_182_2011.txt", encoding="utf-8") as f:
        docs.append(parser.parse_document("Regulation (EU) No 182/2011", f.read()))

    with open("./resources/eu_documents/regulation_ev_765_2008.txt", encoding="utf-8") as f:
        docs.append(parser.parse_document("Regulation (EC) No 765/2008", f.read()))

    with open("./resources/eu_documents/directive_2002_58_ec.txt", encoding="utf-8") as f:
        docs.append(parser.parse_document("Directive 2002/58/EC", f.read()))

    with open("./resources/eu_documents/regulation_ec_1049_2001.txt", encoding="utf-8") as f:
        docs.append(parser.parse_document("Regulation (EC) No 1049/2001", f.read()))

    document_root = Root(children=docs)
    for doc in document_root.children:
        doc.parent = document_root

    actual_references = []

    for node in pre_order(gdpr):
        refs = reference_detector.detect(node.content)
        actual_references.extend(resolver.resolve_single(node, refs))

    with open("./resources/evaluation_data/gdpr_resolved.json", encoding="utf-8") as f:
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

        if not expected_reference["patterns"]:
            print(f"No patterns provided for reference '{actual_reference.text_content}'")
            continue

        if len(expected_reference["patterns"]) != len(resolved):
            print(
                f"Expected {len(expected_reference['patterns'])} solutions for "
                f"reference '{actual_reference.text_content}'. But found {len(resolved)}.")

            if actual_reference.text_content == "Articles 15, 16, 18, 19, 20 and 21":
                print("!!!")
                print(actual_reference.reference_qualifier)
            continue

        for pattern, solution in zip(expected_reference["patterns"], resolved):
            valid, msg = validate(solution, pattern)

            if expected_reference["text"] != actual_reference.text_content:
                print(f"Mismatch between reference text_content and "
                      f"actual text_content. Expected '{expected_reference['text']}' "
                      f"was '{actual_reference.text_content}'")

            if not valid:
                print(
                    f"Found solution for reference '{actual_reference.text_content}' was incorrect.", msg)


def validate(node: Node, pattern: Dict) -> Tuple[bool, str]:
    """
    Validates that a node adheres to a pattern.
    :param node: The node to be tested.
    :param pattern: The pattern to test against
    """

    if not set(pattern.keys()).issubset({"title", "number", "type", "starts_with", "has_child"}):
        print(f"Unrecognized key(s) in pattern '{pattern}'")

    if pattern.get("title") and pattern["title"] != node.title:
        return False, f"Expected title '{pattern['title']}'. Got: '{node.title}'"

    if pattern.get("number") and pattern["number"] != node.number:
        return False, f"Expected number '{pattern['number']}'. Got: '{node.number}'"

    if pattern.get("type") and pattern["type"].lower() != node.__class__.__name__.lower():
        return False, f"Expected type '{pattern['type']}'. Got: '{node.__class__.__name__}'"

    if pattern.get("starts_with") and not node.content.lower().replace(r" ", "").startswith(
        pattern["starts_with"].lower().replace(r" ", "")):
        return False, f"Expected the node to start with '{pattern['starts_with'][:10]}...'. Was: '{node.content[:10]}'."

    if pattern.get("has_child") and not any(validate(n, pattern["has_child"])[0] for n in node.children):
        return False, f"Found no child matching pattern '{pattern['has_child']}'."

    return True, "Valid"


if __name__ == "__main__":
    main()
