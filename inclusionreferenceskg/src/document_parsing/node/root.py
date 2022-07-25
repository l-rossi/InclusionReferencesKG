from typing import Tuple, Optional, Type

from inclusionreferenceskg.src.document_parsing.node.node import Node


class Root(Node):
    """
    Works as the root of a document structure. It must be manually created. Its children should be
    Documents.
    """
    depth = -1

    @classmethod
    def accept_block(cls: Type["Node"], block: str, parent: "Node") -> Tuple[bool, Optional["Root"]]:
        return False, None

    def finalize(self):
        pass
