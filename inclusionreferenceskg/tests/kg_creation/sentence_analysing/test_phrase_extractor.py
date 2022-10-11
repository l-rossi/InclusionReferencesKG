import spacy
from spacy.tokens import Doc, Span, Token

from kg_creation.sentence_analysing.phrase_extractor import PhraseExtractor


def test_extract_from_sentence():
    if not Doc.get_extension("coref_chains"):
        Doc.set_extension("coref_chains", default=None)

    doc = Doc(vocab=spacy.util.get_lang_class("en")().vocab, words=[
        "Article 1(1)", "dictates", "that", "a", "company", "must", "pay", "a", "fine", "if",
        "it", "breaks", "a", "rule"
    ])

    # I pity the people that had to label the training data
    # for spaCy's models
    doc[0].head, doc[0].pos_, doc[0].dep_ = doc[1], "PROPN", "nsubj"
    doc[1].pos_ = "VERB"
    doc[2].head, doc[2].pos_, doc[2].dep_ = doc[6], "SCONJ", "mark"
    doc[3].head, doc[3].pos_, doc[3].dep_ = doc[4], "DET", "det"
    doc[4].head, doc[4].pos_, doc[4].dep_ = doc[6], "NOUN", "nsubj"
    doc[5].head, doc[5].pos_, doc[5].dep_ = doc[6], "AUX", "aux"
    doc[6].head, doc[6].pos_, doc[6].dep_ = doc[1], "VERB", "ccomp"
    doc[7].head, doc[7].pos_, doc[7].dep_ = doc[7], "DET", "det"
    doc[8].head, doc[8].pos_, doc[8].dep_ = doc[6], "NOUN", "dobj"
    doc[9].head, doc[9].pos_, doc[9].dep_ = doc[11], "SCONJ", "mark"
    doc[10].head, doc[10].pos_, doc[10].dep_ = doc[11], "PRON", "nsubj"
    doc[11].head, doc[11].pos_, doc[11].dep_ = doc[6], "VERB", "advcl"
    doc[12].head, doc[12].pos_, doc[12].dep_ = doc[13], "DET", "det"
    doc[13].head, doc[13].pos_, doc[13].dep_ = doc[11], "NOUN", "dobj"

    class MockCoref:
        def resolve(self, x):
            if x == doc[10]:
                return [doc[4]]
            return []

    doc._.coref_chains = MockCoref()

    phrases = PhraseExtractor().extract_from_sentence(Span(doc, 0, len(doc)))

    for p in phrases:
        p.pprint()

    assert len(phrases) == 1, f"Found {len(phrases)} phrases. Expected exactly 1."
    phrase = phrases[0]

    assert len(phrase.agent_objects) == 1
    assert len(phrase.agent_phrases) == 0
    assert len(phrase.condition_phrases) == 0
    assert len(phrase.patient_objects) == 0
    assert len(phrase.patient_phrases) == 1
    assert phrase.agent_objects[0].token == doc[0]

    patient_phrase = phrase.patient_phrases[0]
    assert len(patient_phrase.agent_objects) == 1
    assert patient_phrase.agent_objects[0].token == doc[4]
    assert len(patient_phrase.agent_phrases) == 0
    assert len(patient_phrase.condition_phrases) == 1
    assert len(patient_phrase.patient_objects) == 1
    assert len(patient_phrase.patient_phrases) == 0

    conditional_phrase = patient_phrase.condition_phrases[0]
    assert len(conditional_phrase.agent_objects) == 1
    assert conditional_phrase.agent_objects[0].token == doc[4]
    assert len(conditional_phrase.agent_phrases) == 0
    assert len(conditional_phrase.condition_phrases) == 0
    assert len(conditional_phrase.patient_objects) == 1
    assert conditional_phrase.patient_objects[0].token == doc[13]
    assert len(conditional_phrase.patient_phrases) == 0
