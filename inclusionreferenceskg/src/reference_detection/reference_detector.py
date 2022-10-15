from abc import abstractmethod, ABC
from typing import Dict, List, Type

from spacy.tokens import Span, Doc

from util.reference import Reference


class ReferenceDetector(ABC):
    """
    Contract on how ReferenceDetectors should be interfaced.
    """

    _spacy_components: Dict[Type["ReferenceDetector"], str]

    @abstractmethod
    def detect(self, text: str) -> List[Reference]:
        raise NotImplementedError()

    @staticmethod
    def _spacy_pipe_component_base(reference_detector: "ReferenceDetector"):
        """
        Utility for adapting a ReferenceDetector to a spacy pipeline component or a factory.
        """

        def reference_detector_component(doc: Doc):
            def reference_to_span(reference: Reference):
                s = doc.char_span(reference.start, reference.start + len(reference.text_content))
                if not s:
                    print(f"Could not create span for reference {reference}")
                    return None

                return Span(doc, start=s.start, end=s.end, label="REFERENCE")

            refs = [(ref, reference_to_span(ref)) for ref in reference_detector.detect(doc.text)]
            refs = [x for x in refs if x[1]]

            with doc.retokenize() as retokenizer:
                for ref, span in refs:
                    retokenizer.merge(span, attrs={"POS": "PROPN", "TAG": "REF", "_": {"reference": ref}})

            return doc

        return reference_detector_component
