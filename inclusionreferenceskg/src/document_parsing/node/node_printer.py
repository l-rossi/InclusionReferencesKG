import typing

from document_parsing.node.node import Node
from document_parsing.node.node_traversal import pre_order


def print_nodes(start: Node, indent: int = 3, content_preview_length: int = 20,
                output: typing.Callable[[str, ], typing.Any] = print):
    """Prints the node and its children in pre-order."""

    for curr in pre_order(start):
        if not curr.content:
            curr_content_out = ""
        elif len(curr.content) <= content_preview_length:
            curr_content_out = " " + curr.content
        else:
            curr_content_out = " " + curr.content[:content_preview_length] + "..."

        curr_title = f" [{curr.title}]" if curr.title else ""
        output(
            " " * curr.depth * indent
            + curr.__class__.__name__
            + f" {curr.number}" + curr_title
            + ":" + curr_content_out)
