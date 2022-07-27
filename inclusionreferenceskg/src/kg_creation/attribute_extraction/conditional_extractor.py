import warnings

from inclusionreferenceskg.src.kg_creation.attribute_extraction.attribute_extractor import AttributeExtractor
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import Phrase


class ConditionalExtractor(AttributeExtractor):
    warnings.warn("ConditionalExtractor is deprecated. Instead use the inbuilt functionality of PhraseExtractor",
                  DeprecationWarning)

    def _accept(self, phrase: Phrase):

        for predicate in phrase.predicate:
            if any(tok.dep_ in {"mark", "advmod"} and tok.pos_ == "SCONJ" for tok in predicate.token.lefts):
                phrase.is_conditional = True
                break
