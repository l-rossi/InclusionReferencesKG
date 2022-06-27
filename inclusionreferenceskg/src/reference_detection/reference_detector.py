import typing
from abc import abstractmethod, ABC

from inclusionreferenceskg.src.reference import Reference


class ReferenceDetector(ABC):
    """
    Contract on how ReferenceDetectors should be interfaced.
    """

    @abstractmethod
    def detect(self, text: str) -> typing.List[Reference]:
        raise NotImplementedError()
