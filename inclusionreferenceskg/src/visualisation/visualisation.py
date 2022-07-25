import graphviz

from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.node_traversal import pre_order


def main():
    gdpr = DocumentTreeParser().parse_from_eu_doc_file("GDPR", "gdpr.txt")

    graph = graphviz.Digraph("GDPR", engine="twopi", format="svg")
    graph.graph_attr["ranksep"] = "20"
    graph.graph_attr["overlap"] = "true"

    for node in pre_order(gdpr):
        graph.node(node.id, str(node.immutable_view()), tooltip=node.content)
        if node.parent is not None:
            graph.edge(node.parent.id, node.id)

    graph.render(directory='output/graphs', view=False)


if __name__ == "__main__":
    main()
