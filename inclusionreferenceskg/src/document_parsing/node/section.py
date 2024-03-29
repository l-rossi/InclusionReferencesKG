import re
import typing
from typing import Tuple, Optional

from document_parsing.node.chapter import Chapter
from document_parsing.node.node import Node


class Section(Node):
    depth = Chapter.depth + 1
    ignore_when_forming_full_qualifier = True
    _pattern: typing.ClassVar[re.Pattern] = re.compile(r"Section\s*([1-9][0-9]*)", re.I)

    @classmethod
    def accept_block(cls, block: str, parent: "Node") -> Tuple[bool, Optional["Section"]]:
        match = re.match(Section._pattern, block)

        if not match:
            return False, None

        number = int(match.group(1))
        section = Section(number=number)
        return True, section

    def finalize(self):
        self.title = self.content.strip()
        self.content = ""
