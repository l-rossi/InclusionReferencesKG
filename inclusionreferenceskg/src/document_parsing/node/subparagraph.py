import typing
import warnings

from document_parsing.node.node import Node
from document_parsing.node.paragraph import Paragraph


class Subparagraph(Node):
    depth = Paragraph.depth + 1

    @classmethod
    def accept_block(cls, block: str, parent: Node) -> typing.Tuple[bool, typing.Optional["Node"]]:
        if parent.__class__.depth >= Paragraph.depth:
            return True, Subparagraph(number=len(parent.children) + 1, content=block)

        return False, None

    def finalize(self):
        for i, sibling in enumerate(self.parent.children, 1):
            if self.id == sibling.id:
                self.number = i
                break
        else:
            warnings.warn(f"Could not find self in children of parent. For subparagraph {self.immutable_view()}.")
