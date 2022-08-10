from abc import abstractmethod, ABC

from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import Phrase


class AttributeExtractor(ABC):

    @abstractmethod
    def _accept(self, phrase: Phrase):
        """
        Extract the attributes for a single phrase.

        :param phrase: The phrase for which to extract attributes.
        """
        pass

    def accept_with_children(self, phrase: Phrase):
        """
        Extract the attributes for a phrase and all its children.

        :param phrase: The phrase for which to extract attributes.
        """
        self._accept(phrase)
        for p in phrase.patient_phrases + phrase.condition_phrases + phrase.agent_phrases:
            self._accept(p)
