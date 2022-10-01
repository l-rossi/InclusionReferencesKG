import re
import typing

from document_parsing.preprocessing.block_preprocessor import \
    BlockPreprocessor


class HeaderPreprocessor(BlockPreprocessor):
    """
    Used to try and filter out the headers of documents.
    """
    date_pattern = re.compile(r"[0-9]{1,2}\.[0-9]{1,2}\.[1-9][0-9]{3}")

    @staticmethod
    def process(blocks: typing.List[str]):
        # Heuristic for removing blocks based on removing those starting with a date. TODO: Discuss applicability
        return [block for block in blocks if not HeaderPreprocessor.date_pattern.match(block)]
