from inclusionreferenceskg.src.kg_creation.attribute_extraction.attribute_extractor import AttributeExtractor
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import Phrase


class ConditionalExtractor(AttributeExtractor):

    def _accept(self, phrase: Phrase):
        for predicate in phrase.predicate:
            if any(1 for tok in predicate.token.lefts if tok.dep_ in {"mark", "advmod"} and tok.pos_ == "SCONJ"):
                phrase.is_conditional = True
                break
