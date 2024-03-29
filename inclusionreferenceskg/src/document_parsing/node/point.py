import re
import typing

from document_parsing.node.node import Node
from document_parsing.node.subparagraph import Subparagraph
from util.util import alph_to_dec


class Point(Node):
    depth = Subparagraph.depth + 1
    _pattern: typing.ClassVar[re.Pattern] = re.compile(r"^\(([a-z]|ii)\).*?$", re.I)

    @classmethod
    def accept_block(cls, line: str, _) -> typing.Tuple[bool, typing.Optional["Point"]]:
        match = re.match(Point._pattern, line)

        if not match:
            return False, None

        # Points are ordered using the alphabet. We convert this ordering to numerals: a->1, b->2, ...
        number = alph_to_dec(match.group(1))
        point = Point(number=number, content=line)
        return True, point

    def finalize(self):
        pass
