import typing
from abc import abstractmethod, ABC


class ReferenceDetector(ABC):
    """
    Contract on how ReferenceDetectors should be interfaced.
    """

    @abstractmethod
    def detect(self, text: str) -> typing.List[str]:
        raise NotImplementedError()
