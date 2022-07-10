import csv
import typing

from inclusionreferenceskg.src.reference import Reference
from inclusionreferenceskg.src.reference_detection.reference_detector import ReferenceDetector


class GoldStandardReferenceDetector(ReferenceDetector):
    """
    Implements a reference detector based on getting references from a csv file.

    Note: This is a one-time use detector for the references in a file. Further,
    all calls to detect must be done in order that the references occur in the document.

    This is not a fool proof implementation, as it does not consider the position of
    the gold standard reference put rather tries to greedily produce references.
    """

    def __init__(self, file_location: str, delimiter: str = ";"):
        """
        :param file_location: The location of the file with the references that are detected.\
        The first line is ignored as the header.
        :param delimiter: The delimiter used for the CSV file.
        """
        assert file_location.endswith(".csv"), f"{self.__class__} requires a CSV file to work with."

        with open(file_location, "r", encoding="utf-8") as ef:
            self.expected_references = [x[0] for x in csv.reader(ef, delimiter=delimiter)][1:]

    def detect(self, text: str) -> typing.List[Reference]:
        def _gen():
            text_inner = text
            total_offset = 0

            while self.expected_references and (ind := text_inner.find(self.expected_references[0])) != -1:
                yield Reference(start=total_offset + ind, text_content=self.expected_references.pop(0))
                total_offset += ind
                text_inner = text_inner[ind+1:]

        return list(_gen())
