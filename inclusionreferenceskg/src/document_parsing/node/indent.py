import re
import warnings
from typing import ClassVar
from typing import Tuple, Optional

from document_parsing.node.node import Node
from document_parsing.node.point import Point


class Indent(Node):
    depth = Point.depth + 1
    _pattern: ClassVar[re.Pattern] = re.compile(r"^- .*?$", re.I)

    @classmethod
    def accept_block(cls, block: str, parent: Node) -> Tuple[bool, Optional["Node"]]:
        match = re.match(Indent._pattern, block)

        if not match:
            return False, None

        return True, Indent(content=block)

    def finalize(self):
        for i, sibling in enumerate(self.parent.children, 1):
            if self.id == sibling.id:
                self.number = i
                break
        else:
            warnings.warn(f"Could not find self in children of parent. For indent {self.immutable_view()}.")
