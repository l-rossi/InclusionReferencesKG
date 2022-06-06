import re
import typing

from inclusionreferenceskg.inclusionreferenceskg.document_parsing.node.chapter import Chapter
from inclusionreferenceskg.inclusionreferenceskg.document_parsing.node.node import Node


class Article(Node):
    depth = Chapter.depth + 1
    _pattern: typing.ClassVar[re.Pattern] = re.compile(r"^Article ([1-9][0-9]*)\s*$", re.I)

    @classmethod
    def accept_block(cls, line: str, _) -> typing.Tuple[bool, typing.Optional["Article"]]:
        match = re.match(Article._pattern, line)

        if not match:
            return False, None

        number = int(match.group(1))
        paragraph = Article(number=number)
        return True, paragraph

    def finalize(self):
        split_content = [l.strip() for l in self.content.split("\n") if l.strip()]
        self.title = split_content[0]
        self.content = "\n".join(split_content[1:])
