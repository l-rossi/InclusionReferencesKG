import typing
from abc import ABC, abstractmethod


class BlockPreprocessor(ABC):
    """
    ABC for processing a list of text blocks which are subsequently parsed.
    Used mostly for filtering undesirable blocks.
    """

    @staticmethod
    @abstractmethod
    def process(blocks: typing.List[str]) -> typing.List[str]:
        raise NotImplementedError()
