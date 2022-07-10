import re
import typing

from inclusionreferenceskg.src.document_parsing.preprocessing.block_preprocessor import BlockPreprocessor
from inclusionreferenceskg.src.util.regex_util import RegexUtil


class InitialSpacePreprocessor(BlockPreprocessor):
    """
    Inserts a space between a paragraphs numbering and the text of the numbering.

    Example:
    1.This paragraph...
    ->
    1. This paragraph
    """

    @staticmethod
    def process(blocks: typing.List[str]) -> typing.List[str]:
        def map_block(block):
            if match := re.match(fr"^(?:{RegexUtil.number}\.|{RegexUtil.para})\S", block):
                return block[:match.end() - 1] + " " + block[match.end() - 1:]
            return block

        return [map_block(block) for block in blocks]
