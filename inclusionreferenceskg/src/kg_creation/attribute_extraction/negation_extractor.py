from __future__ import annotations

from inclusionreferenceskg.src.kg_creation.attribute_extraction.attribute_extractor import AttributeExtractor
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import Phrase


class NegationExtractor(AttributeExtractor):

    def _accept(self, phrase: Phrase):
        for p in phrase.predicate:
            p.negated = sum(1 for tok in p.token.rights if tok.dep_ == "neg") % 2 == 0
