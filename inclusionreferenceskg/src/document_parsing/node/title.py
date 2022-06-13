import re
import typing

from inclusionreferenceskg.src.document_parsing.node.node import Node
from inclusionreferenceskg.src.document_parsing.node.regulation import Regulation
from inclusionreferenceskg.src.util.util import rom_to_dec


class Title(Node):
    depth = Regulation.depth + 1
    _pattern: typing.ClassVar[re.Pattern] = re.compile(r"^Title ([IVXLCDM]+)\s*$", re.I)

    @classmethod
    def accept_block(cls, block: str, _) -> typing.Tuple[bool, typing.Optional["Title"]]:
        match = re.match(Title._pattern, block)

        if not match:
            return False, None

        number = rom_to_dec(match.group(1))
        paragraph = Title(number=number)
        return True, paragraph

    def finalize(self):
        if self.content.strip():
            split_content = [l.strip() for l in self.content.split("\n") if l.strip()]
            self.title = split_content[0]
            self.content = "\n".join(split_content[1:])
