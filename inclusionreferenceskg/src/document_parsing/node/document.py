import typing

from inclusionreferenceskg.src.document_parsing.node.node import Node


class Document(Node):
    """
    This class acts as a node for all document types including: regulations, treaties, directives.
    As there is no distinction between these documents when resolving references, one class suffices.
    """
    depth = 0

    @classmethod
    def accept_block(cls, *_) -> typing.Tuple[bool, typing.Optional["Document"]]:
        return False, None

    def finalize(self):
        pass
