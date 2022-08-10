from typing import Tuple, Generator

from spacy.tokens import Doc, Span, Token

from inclusionreferenceskg.src.document_parsing.node.node import Node


def pre_order(root: Node):
    """
    Iterates through each node reachable from the root node in pre order.
    No checks for infinite recursion are made.

    :param root: The node to start at.
    """

    dfs_stack = [root]
    while dfs_stack:
        curr = dfs_stack.pop()
        dfs_stack.extend(curr.children[::-1])
        yield curr


def traverse_doc_by_node(doc: Doc) -> Generator[Tuple[Node, Span], None, None]:
    """
    Iterates a doc object by the nodes.
    :param doc: The doc to be iterated.
    :return: A generator of tuples.
    """

    if not Token.get_extension("node"):
        raise ValueError("Tokens must have the node attribute for iterating.")

    prev_node = None
    last_span_end = 0
    for i, tok in enumerate(doc):
        if prev_node and tok._.node.id != prev_node.id:
            yield prev_node, Span(doc, last_span_end, i)
            last_span_end = i
        prev_node = tok._.node
    yield prev_node, Span(doc, last_span_end, len(doc))
