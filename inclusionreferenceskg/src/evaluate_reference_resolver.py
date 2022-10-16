import json
import logging
from typing import Dict, Tuple

from document_parsing.document_tree_parser import DocumentTreeParser
from document_parsing.node.node import Node
from document_parsing.node.node_traversal import pre_order
from evaluation.stat_accumulator import StatAccumulator
from reference_detection.gold_standard_reference_detector import GoldStandardReferenceDetector
from reference_resolution.reference_resolver import ReferenceResolver
from util.parser_util import gdpr_dependency_root


def main():
    # We do not calculate the F1 score as we do not deem it necessary for such good results.
    resolver = ReferenceResolver()
    stat_acc = StatAccumulator()

    parser = DocumentTreeParser()
    reference_detector = GoldStandardReferenceDetector("./resources/evaluation_data/gdpr_references.csv")

    gdpr, document_root = gdpr_dependency_root(parser)

    actual_references = []

    for node in pre_order(gdpr):
        refs = reference_detector.detect(node.content)
        actual_references.extend(resolver.resolve_single(node, refs))

    with open("./resources/evaluation_data/gdpr_resolved.json", encoding="utf-8") as f:
        expected_references = json.load(f)

    stat_acc.n_expected = sum(map(lambda x: len(x["patterns"]), expected_references))
    print("Number of tested references:", len(expected_references))
    print("Number of referenced nodes:", sum(map(lambda x: len(x["patterns"]), expected_references)))

    for actual_reference, expected_reference in zip(actual_references, expected_references):
        stat_acc.n_detected += len(actual_reference.reference_qualifier)
        if "patterns" not in expected_reference:
            logging.warning(f"Skipping evaluation for '{expected_reference.get('text')}'. No patterns found.")
            continue

        if (l := len(actual_reference.reference_qualifier)) == 0:
            print(
                f"ReferenceResolver produced {l} reference qualifiers for reference '{actual_reference.text_content}'. "
                f"Expected 1.")
            stat_acc.false_negatives += len(expected_reference["patterns"])
            continue

        resolved = []
        for reference_qualifier in actual_reference.reference_qualifier:
            resolved_single = document_root.resolve_loose(reference_qualifier)
            if len(resolved_single) == 0:
                print(f"Could not resolve '{actual_reference.text_content}'. "
                      f"Qualifier: '{actual_reference.reference_qualifier}'.")
                stat_acc.false_negatives += len(expected_reference["patterns"])
                continue

            if len(resolved_single) > 1:
                print(
                    f"Found multiple solutions to reference '{actual_reference.text_content}'. Further testing is "
                    f"done only against the first resolved node.")
                stat_acc.false_positives += len(resolved_single)
                stat_acc.false_negatives += len(expected_reference["patterns"])
            resolved.append(resolved_single[0])

        if not expected_reference["patterns"]:
            logging.warning(f"No patterns provided for reference '{actual_reference.text_content}'")
            continue

        if len(expected_reference["patterns"]) != len(resolved):
            print(
                f"Expected {len(expected_reference['patterns'])} solutions for "
                f"reference '{actual_reference.text_content}'. But found {len(resolved)}.")
            stat_acc.false_positives += len(resolved)
            stat_acc.false_negatives += len(expected_reference["patterns"])
            continue

        for pattern, solution in zip(expected_reference["patterns"], resolved):
            valid, msg = validate(solution, pattern)

            if expected_reference["text"] != actual_reference.text_content:
                print(f"Mismatch between reference text_content and "
                      f"actual text_content. Expected '{expected_reference['text']}' "
                      f"was '{actual_reference.text_content}'")
                stat_acc.false_negatives += 1
                stat_acc.false_positives += 1
                continue

            if not valid:
                print(
                    f"Found solution for reference '{actual_reference.text_content}' was incorrect.", msg)
                stat_acc.false_negatives += 1
                stat_acc.false_positives += 1

    print(f"Precision: {stat_acc.precision():4.3f}, Recall: {stat_acc.recall():4.3f}, F1: {stat_acc.f1():4.3f}")


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
