import re
import typing

from inclusionreferenceskg.src.document_parsing.node.node import Node
from inclusionreferenceskg.src.document_parsing.node.paragraph import Paragraph


class Subparagraph(Node):
    depth = Paragraph.depth + 1
    _pattern: typing.ClassVar[re.Pattern] = re.compile(r"^(?:([1-9][0-9]*)\.|\(([1-9][0-9]*)\)) .*?$", re.I)

    @classmethod
    def accept_block(cls, block: str, parent: Node) -> typing.Tuple[bool, typing.Optional["Node"]]:
        if parent.__class__.depth >= Paragraph.depth:
            return True, Subparagraph(number=len(parent.children) + 1, content=block)

        return False, None

    def finalize(self):
        self.number = self.parent.children.index(self) + 1

