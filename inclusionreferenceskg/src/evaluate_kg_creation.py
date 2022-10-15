import csv

from document_parsing.node.article import Article
from evaluation.stat_accumulator import StatAccumulator
from kg_creation.kg_renderer import create_graph
from kg_creation.knowledge_graph import KnowledgeGraph
from util.parser_util import gdpr_dependency_root


def evaluate(stat_accumulator: StatAccumulator, graph: KnowledgeGraph, expected_file: str):
    """
    Evaluates a subset of a document against a standard.
    KG is relatively subjective, at least if not done by a professional as is the case here.
    Thus this evaluation does not have great validity.


    Limitations:
    This evaluation does not take into consideration:
    - Entity Linking
    - Structure / References
    """
    with open(expected_file, "r", encoding="utf-8") as ef:
        expected = {tuple(x) for x in csv.reader(ef, delimiter=",")}

    actual = {(x[1], y, z[1]) for x, y, z in graph.as_triplets() if y not in {"defines", "contains"}}

    for a in actual:
        if a not in expected:
            stat_accumulator.false_positives += 1
            print(f"Produced unexpected '{a}'")

    for e in expected:
        if e not in actual:
            stat_accumulator.false_negatives += 1
            print(f"Did no find expected: '{e}'")

    stat_accumulator.n_detected_references += len(actual)
    stat_accumulator.n_expected_references += len(expected)


if __name__ == "__main__":
    stat_acc = StatAccumulator()

    gdpr, document_root = gdpr_dependency_root()
    article29 = gdpr.resolve_loose([Article(number=29)])[0]
    article30 = gdpr.resolve_loose([Article(number=30)])[0]
    actual29 = create_graph(article29, article29, fast=False)
    actual30 = create_graph(article30, article30, fast=False)

    evaluate(stat_acc, actual29, "./resources/evaluation_data/kg_triplets/gdpr_article_29.csv")
    evaluate(stat_acc, actual30, "./resources/evaluation_data/kg_triplets/gdpr_article_30.csv")

    print(f"Precision: {stat_acc.precision():4.3f}, Recall: {stat_acc.recall():4.3f}, F1: {stat_acc.f1():4.3f}")
