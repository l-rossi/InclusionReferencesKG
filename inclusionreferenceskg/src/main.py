from document_parsing.node.article import Article
from kg_creation.kg_renderer import create_graph
from util.parser_util import gdpr_dependency_root

if __name__ == "__main__":
    gdpr, document_root = gdpr_dependency_root()
    article6 = gdpr.resolve_loose([Article(number=30)])[0]

    graph = create_graph(document_root, document_root, fast=True)
    print(len(graph.nodes))
    print(print(sum(len(x.adj) for x in graph.nodes.values())))

