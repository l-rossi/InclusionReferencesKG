import typing

from inclusionreferenceskg.src.document_parsing.node.node import Node


class Document(Node):
    """
    This class acts as a node for all document types including: regulations, treaties, directives.
    As there is no distinction between these documents when resolving references, one class suffices.
    """
    depth = 0

    @classmethod
    def accept_block(cls, *_) -> typing.Tuple[bool, typing.Optional["Document"]]:
        return False, None

    def _pattern_match(self, pat: "Node"):
        wildcard = -1
        type_match = pat is None or pat.__class__ == self.__class__
        number_match = pat is None or pat.number == self.number or pat.number == wildcard

        # We are more lenient when matching the title of a regulation. Normalization of the title may also be
        # feasible.
        title_match = pat is None or pat.title == self.title or pat.title is None or pat.title == wildcard or \
                      pat.title.lower() in self.title.lower() or self.title.lower() in pat.title.lower()

        return type_match and number_match and title_match

    def finalize(self):
        pass
