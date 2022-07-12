import re
from typing import List, Set

import spacy
from spacy import Language
from spacy import displacy
from spacy.tokens import Span, Token
from textacy import constants

from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.article import Article
from inclusionreferenceskg.src.document_parsing.node.node_traversal import pre_order
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import Predicate, Phrase, PhraseObject
from inclusionreferenceskg.src.reference_detection.regex_reference_detector import RegexReferenceDetector

# spacy.prefer_gpu()


# https://stackoverflow.com/questions/39763091/how-to-extract-subjects-in-a-sentence-and-their-respective-dependent-phrases
# Categories thanks to psr's answer on Stackoverflow https://stackoverflow.com/a/40014532/9885004
SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
OBJECTS = ["dobj", "dative", "attr", "oprd"]
ADJECTIVES = ["acomp", "advcl", "advmod", "amod", "appos", "nn", "nmod", "ccomp", "complm",
              "hmod", "infmod", "xcomp", "rcmod", "poss", " possessive"]
COMPOUNDS = ["compound"]
PREPOSITIONS = ["prep"]

# Constants based on textacy's constants
SUBJ_DEPS: Set[str] = {"agent", "csubj", "csubjpass", "expl", "nsubj", "nsubjpass"}
OBJ_DEPS: Set[str] = {"attr", "dobj", "dative", "oprd", "pobj"}
AUX_DEPS: Set[str] = {"aux", "auxpass", "neg"}


@Language.component("reference_detector_component")
def reference_detector_component(doc: spacy.tokens.Doc):
    def match_to_span(match: re.Match):
        s = doc.char_span(match.start(), match.end())
        if not s:
            print(f"Could not create span for match {match}")
            return None

        return Span(doc, start=s.start, end=s.end, label="REFERENCE")

    refs = [match_to_span(match) for match in re.finditer(RegexReferenceDetector._build_pattern(), doc.text)]
    refs = [x for x in refs if x]
    if "sc" not in doc.spans:
        doc.spans["sc"] = []
    doc.spans["sc"] += refs
    return doc


@Language.component("noun_phrase_component")
def noun_phrase_component(doc: spacy.tokens.Doc):
    if "sc" not in doc.spans:
        doc.spans["sc"] = []
    doc.spans["sc"] += [Span(doc, start=np.start, end=np.end, label="PROPER_NOUN") for np in doc.noun_chunks]

    return doc


def main():
    with open("./resources/eu_documents/gdpr.txt", encoding="utf-8") as f:
        gdpr_text = f.read()

    gdpr = DocumentTreeParser().parse_document("GDPR", gdpr_text)

    article38 = gdpr.resolve_loose([Article(number=38)])[0]

    txt = ""
    for node in list(pre_order(article38)):
        if node.content:
            txt += node.content + "\n"

    # nlp = spacy.load("en_core_web_trf")
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("reference_detector_component", before="ner")
    # nlp.add_pipe("noun_phrase_component", before="ner")
    nlp.remove_pipe("ner")

    # print(nlp.analyze_pipes(pretty=True))

    doc = nlp(txt)
    """doc = nlp("If the dog is red, the cat is green. When the door opens, I will go through. Should I be green, I will buy a house. I shall be green.")

    for token in doc:
        print(token, token.pos_, token.tag_)

    displacy.serve(doc, "dep")

    exit()"""

    for sent in doc.sents:
        import textacy.spacier.utils as spacy_utils
        main_verbs_of_sent = get_main_verbs_of_sent(sent)

        phrases: List[Phrase] = [Phrase(predicate=[Predicate(token=verb) for verb in verb_group]) for verb_group in
                                 main_verbs_of_sent]
        print("1")
        print([type(v) for v in phrases])

        for phrase in phrases:
            for predicate in phrase.predicate:
                # Add auxilaries, preds, negations
                pass

        print("START OF SENTENCE")
        print(sent)
        # print(main_verbs_of_sent)

        # subjects
        # print("subjects")
        # TODO subjects missing compunds
        # TODO Verbs missing negations, auxilaries
        for phrase in phrases:
            is_passive = phrase.predicate[0].token.tag_ == "VBN"
            phrase.agent = [PhraseObject(tok) for tok in spacy_utils.get_subjects_of_verb(phrase.predicate[0].token)]

            verb_as_patient = [tok for tok in phrase.predicate[0].token.rights if tok.dep_ == "ccomp"]
            # TODO: Please refactor. This is giving me nightmares. D,:
            phrase_as_patient = []
            for vap in verb_as_patient:
                for p in phrases:
                    for pred in p.predicate:
                        if pred.token == vap:
                            phrase_as_patient.append(p)
                            break
            print([type(v) for v in phrase_as_patient])
            print("2")
            print([type(v) for v in phrases])

            if phrase_as_patient and is_passive:
                raise Exception("Phrase as a patient cannot coincide with a passive voice.")

            grammatical_object = get_objects_of_verb_consider_preposition(phrase.predicate[0].token)

            if grammatical_object and phrase_as_patient:
                raise Exception("Found both an object and a ccomp for a predicate.")

            phrase.patient = [PhraseObject(token=tok) for tok in grammatical_object] or phrase_as_patient

            # If the patient of a phrase is also the

            """print(, verb_group,
            [tok for tok in verb_group[0].rights if
             tok.dep_ == "ccomp"] + get_objects_of_verb_consider_preposition(
                verb_group[0]))"""
            #print(phrase.pprint())
            print(phrase)
        """print("Sentence:", sentence)
        root = sentence.root

        predicate = [root] + [token for token in sentence if token.head == root and (
            token.dep_ in ["prep"]
        )]

        subj = [token for token in doc if token.head in predicate and token.dep_ in SUBJECTS]

        subj_len = 0
        while len(subj) != subj_len:
            subj += [token for token in doc if
                     token.dep_ == "conj"
                     and token.head in subj]
            subj_len = len(subj)

        print("pred", predicate)
        print("subj", subj)


        # objects"""

    """for token in doc:
        print(token.orth_, token.dep_, token.head.orth_, [t.orth_ for t in token.lefts],
              [t.orth_ for t in token.rights])"""

    displacy.serve(doc, "dep", options={"colors": {"REFERENCE": "red", "PROPER_NOUN": "cyan"}})


def get_main_verbs_of_sent(sent: Span) -> List[List[Token]]:
    """Return the main (non-auxiliary) verbs in a sentence."""
    return [
        [tok] + _get_conjuncts(tok) for tok in sent if tok.pos_ == "VERB" and tok.dep_ not in constants.AUX_DEPS
    ]


def get_objects_of_verb_consider_preposition(verb: Token) -> List[Token]:
    """
    Adapted from get_objects_of_verb from textacy.

    Return all objects of a verb according to the dependency parse,
    including open clausal complements.
    """
    verb_and_prep = [verb] + [tok for tok in verb.rights if tok.dep_ == "prep"]
    objs = [tok for v in verb_and_prep for tok in v.rights if tok.dep_ in OBJ_DEPS]
    objs.extend(tok for tok in verb.rights if tok.dep_ == "xcomp")
    objs.extend(tok for obj in objs for tok in _get_conjuncts(obj))
    return objs


def _get_conjuncts(tok: Token) -> List[Token]:
    """
    Return conjunct dependents of the leftmost conjunct in a coordinated phrase,
    e.g. "Burton, [Dan], and [Josh] ...".
    """
    return [right for right in tok.rights if right.dep_ == "conj"]


# TODO Remove
if __name__ == "__main__":
    main()
