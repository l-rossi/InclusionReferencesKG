import re
import typing

from document_parsing.node.article import Article
from document_parsing.node.node import Node


class Paragraph(Node):
    depth = Article.depth + 1
    _pattern: typing.ClassVar[re.Pattern] = re.compile(r"^(?:([1-9][0-9]*)\.|\(([1-9][0-9]*)\))\s?.*?$", re.I)
    consumes = False

    @classmethod
    def accept_block(cls, block: str, _) -> typing.Tuple[bool, typing.Optional["Paragraph"]]:
        match = re.match(Paragraph._pattern, block)

        if not match:
            return False, None

        number = int(match.group(1) or match.group(2))
        # The block is not added as content as we want it to be captured by a subparagraph.
        paragraph = Paragraph(number=number)
        return True, paragraph

    def finalize(self):
        pass
