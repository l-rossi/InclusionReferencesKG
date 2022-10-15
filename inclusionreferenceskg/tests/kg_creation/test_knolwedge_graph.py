from document_parsing.node.article import Article
from kg_creation.knowledge_graph import KnowledgeGraph, BatchedMerge


def test_batched_merge():
    graph = KnowledgeGraph()
    graph.add_node("1", Article())
    graph.add_node("2", Article())
    graph.add_node("3", Article())

    graph.add_node("4", Article())
    graph.add_node("5", Article())
    graph.add_node("6", Article())

    with BatchedMerge(graph) as proxy_graph:
        proxy_graph.merge("1", "2")
        proxy_graph.merge("2", "3")
        proxy_graph.merge("3", "1")

        # If merges are not batched, these matches
        # cannot be done to already merged nodes.
        proxy_graph.merge("4", "1")
        proxy_graph.merge("5", "2")
        proxy_graph.merge("6", "3")

    assert len(graph.nodes) == 1


def test_batch_merge_components():
    graph = KnowledgeGraph()
    for i in range(1, 13):
        graph.add_node(str(i), Article())

    with BatchedMerge(graph) as proxy_graph:
        proxy_graph.merge("1", "2")
        proxy_graph.merge("2", "3")
        proxy_graph.merge("3", "4")
        proxy_graph.merge("2", "4")

        proxy_graph.merge("5", "6")
        proxy_graph.merge("6", "7")

        proxy_graph.merge("9", "10")
        proxy_graph.merge("9", "11")
        proxy_graph.merge("9", "12")
        proxy_graph.merge("10", "11")
        proxy_graph.merge("10", "12")
        proxy_graph.merge("11", "12")

    assert len(graph.nodes) == 4
    ids = sorted(int(x) for x in graph.nodes.keys())
    assert ids[0] in {1, 2, 3, 4}
    assert ids[1] in {5, 6, 7}
    assert ids[2] == 8
    assert ids[3] in {9, 10, 11, 12}


def test_merge_override():
    graph = KnowledgeGraph()

    graph.add_node("u", Article(id="1"))
    graph.add_node("v", Article(id="2"))

    graph.add_node("o1", Article(id="3"))
    graph.add_node("o2", Article(id="4"))
    graph.add_node("o3", Article(id="5"))
    graph.add_node("o4", Article(id="5"))

    graph.add_edge("o1", "u", "dummy")
    graph.add_edge("u", "o2", "dummy")

    graph.add_edge("v", "o3", "dummy")
    graph.add_edge("o4", "v", "dummy")

    graph.merge("u", "v")
    assert "u" in graph.nodes
    assert "v" not in graph.nodes
    assert graph.nodes.get("u").item.id == "1"

    u = graph.nodes.get("u")
    assert "o1" in u.adj_in
    assert "o4" in u.adj_in
    assert "o2" in u.adj.keys()
    assert "o3" in u.adj.keys()

    assert len(u.item_history) == 1
    assert u.item_history[0].id == "2"

