from inclusionreferenceskg.src.kg_creation.attribute_extraction.attribute_extractor import AttributeExtractor
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import Phrase


class PrepositionExtractor(AttributeExtractor):

    def _accept(self, phrase: Phrase):
        for predicate in phrase.predicate:
            predicate.prepositions = [x.text for x in predicate.token.children if x.dep_ == "prep"]
