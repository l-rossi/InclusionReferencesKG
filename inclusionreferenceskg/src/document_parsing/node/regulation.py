import typing

from inclusionreferenceskg.src.document_parsing.node.node import Node


class Regulation(Node):
    depth = 0

    @classmethod
    def accept_block(cls, *_) -> typing.Tuple[bool, typing.Optional["Regulation"]]:
        return False, None

    def finalize(self):
        pass
