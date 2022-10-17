import re
import typing

from document_parsing.node.node import Node
from document_parsing.node.title import Title
from util.regex_util import RegexUtil
from util.util import rom_to_dec


class Chapter(Node):
    depth = Title.depth + 1
    ignore_when_forming_full_qualifier = True
    _pattern: typing.ClassVar[re.Pattern] = re.compile(fr"^Chapter\s({RegexUtil.roman}|{RegexUtil.number})\s*$", re.I)

    @classmethod
    def accept_block(cls, block: str, _) -> typing.Tuple[bool, typing.Optional["Chapter"]]:
        match = re.match(Chapter._pattern, block)

        if not match:
            return False, None

        try:
            number = int(match.group(1))
        except ValueError:
            number = rom_to_dec(match.group(1))

        paragraph = Chapter(number=number)
        return True, paragraph

    def finalize(self):
        if self.content.strip():
            split_content = [l.strip() for l in self.content.split("\n") if l.strip()]
            self.title = split_content[0]
            self.content = "\n".join(split_content[1:])
