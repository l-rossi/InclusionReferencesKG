import re
import typing

from inclusionreferenceskg.src.document_parsing.preprocessing.block_preprocessor import \
    BlockPreprocessor


class FootnoteDeletePreprocessor(BlockPreprocessor):
    """
    Class to resolve footnotes in a EU regulation text body.

    Detected footnotes aredeleted.
    """

    @staticmethod
    def process(blocks: typing.List[str]):

        visited = []

        footnote_start_pattern = re.compile(r"\(([1-9][0-9]*)\)")

        for block in blocks:
            match = footnote_start_pattern.match(block)
            if match:
                # We look for a number in parentheses which is not part of a reference (paragraph):
                footnote_reference_pattern = r"(?<!and|..,) \(" + match.group(1) + r"\)"

                # Look back over the visited blocks.
                for visited_block in visited:
                    if re.search(footnote_reference_pattern, visited_block):
                        # Only delete if we have found a reference to this footnote somewhere.
                        break
                else:
                    visited.insert(0, block)
            else:
                visited.insert(0, block)

        return reversed(visited)
