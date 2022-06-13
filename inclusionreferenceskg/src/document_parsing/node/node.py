import dataclasses
import typing
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Optional, List, Tuple, Type


@dataclass
class Node(ABC):
    """
    Abstract base class for classes that represent parts of EU regulations,
    """

    depth: ClassVar[int]
    consumes: ClassVar[bool] = True

    children: List["Node"] = dataclasses.field(default_factory=list)
    number: Optional[int] = None
    content: Optional[str] = ""
    title: Optional[str] = None
    parent: Optional["Node"] = None

    @classmethod
    @abstractmethod
    def accept_block(cls, block: str, parent: "Node") -> Tuple[bool, Optional["Node"]]:
        """
        Accepts a block of text, checks if it is a start token for this node and returns a node if so.
        It is not the the responsibility of this method to set the parent

        :param parent: The currently active parent.
        :param block: The line to be checked for a start token.
        :return The first element of the tuple indicates if a start
        token was detected, the second one returns the new node if applicable.
        """
        raise NotImplementedError()

    @abstractmethod
    def finalize(self):
        """
        Called when the last bit of content has been added to a node.
        """
        raise NotImplementedError()

    def resolve(self, pattern: List[Optional["Node"]], curr_depth=0) -> List["Node"]:
        """
        Finds nodes that are at the end of the path described by the pattern parameter relative to this node.
        Matches are done on the basis of the node type and the "number". In the pattern, -1 is treated as a wildcard.

        :param pattern: The pattern to be matched.
        :param curr_depth: The current recursion depth.
        :return: A list of potential matches.
        """
        warnings.warn("Node.resolve is deprecated in favor of the slightly differently working Node.resolve_loose.",
                      DeprecationWarning)

        wildcard = -1

        if len(pattern) <= curr_depth:
            return []

        pat = pattern[curr_depth]
        type_match = pat is None or pat.__class__ == self.__class__
        number_match = pat is None or pat.number == self.number or pat.number == wildcard

        if not (type_match and number_match):
            return []

        if (type_match or number_match) and len(pattern) == curr_depth + 1:
            return [self]

        matches = []

        for child in self.children:
            matches.extend(child.resolve(pattern, curr_depth=curr_depth + 1))

        return matches

    def _pattern_match(self, pat: "Node"):
        wildcard = -1
        type_match = pat is None or pat.__class__ == self.__class__
        number_match = pat is None or pat.number == self.number or pat.number == wildcard
        return type_match and number_match

    def resolve_loose(self, pattern: List[Optional["Node"]], pattern_depth=0) -> List["Node"]:
        """
        Finds all children that have the pattern along their path to this node, ignoring additional nodes between
        nodes and before the first node but not after the last node of the pattern.

        Note: This implementation breaks if the pattern contains multiple of the same type of node.
        ToDO: Fact check the statement above.
        """

        if pattern_depth == len(pattern) - 1 and self._pattern_match(pattern[pattern_depth]):
            return [self]

        matches = []

        advance = 1 if self._pattern_match(pattern[pattern_depth]) else 0

        for child in self.children:
            matches.extend(child.resolve_loose(pattern, pattern_depth=pattern_depth + advance))

        return matches