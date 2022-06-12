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
