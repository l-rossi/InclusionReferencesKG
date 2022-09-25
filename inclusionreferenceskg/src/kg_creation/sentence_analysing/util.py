"""
Many of the functions/methods/constants here are based on those created for the 'textacy' library maintained by Burton DeWilde.
Github: https://github.com/chartbeat-labs/textacy. Reference to this library will simply be made be referencing the
library by name.
"""
from typing import List, Set

import textacy.spacier.utils
from spacy.tokens import Span, Token

# https://stackoverflow.com/questions/39763091/how-to-extract-subjects-in-a-sentence-and-their-respective-dependent-phrases
# Categories thanks to psr's answer on Stackoverflow https://stackoverflow.com/a/40014532/9885004
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import Predicate

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


def get_main_verbs_of_sent(sent: Span) -> List[List[Token]]:
    """
    Based on 'get_main_verbs_of_sent' in textacy, but also groups verbs linked by conjunctions

    Return the main (non-auxiliary) verbs in a sentence.
    """

    verbs = [
        set([tok] + get_conjuncts(tok, {"VERB", "AUX"})) for tok in sent if
        tok.pos_ in {"VERB", "AUX"} and tok.dep_ not in AUX_DEPS
    ]

    verbs_out = []

    for vg in verbs:
        for vo in verbs_out:
            if not vo.isdisjoint(vg):
                vo.update(vg)
                break
        else:
            verbs_out.append(vg)

    return [list(x) for x in verbs_out]


def get_objects_of_predicate_consider_preposition(predicate: List[Predicate]) -> List[Token]:
    return get_objects_of_verb_consider_preposition([p.token for p in predicate])


def get_objects_of_verb_consider_preposition(verbs: List[Token]) -> List[Token]:
    """
    Adapted from 'get_objects_of_verb' from textacy.

    Return all objects of a verb according to the dependency parse,
    including open clausal complements.
    """

    objs = []
    for verb in verbs:
        verb_and_prep = [verb] + [tok for tok in verb.rights if tok.dep_ in {"prep", "agent"}]
        objs.extend(tok for v in verb_and_prep for tok in v.rights if tok.dep_ in OBJ_DEPS)
        objs.extend(tok for tok in verb.rights if tok.dep_ == "xcomp")
        objs.extend(tok for tok in verb.rights if tok.dep_ in {"acomp"})
        objs.extend(tok for obj in objs for tok in get_conjuncts(obj, {obj.pos_}))
    return objs


def get_conjuncts(tok: Token, allowed_pos: Set[str] = None) -> List[Token]:
    """
    Adapted from '_get_conjuncts' from textacy.

    Return conjunct dependents of the leftmost conjunct in a coordinated phrase,
    e.g. "Burton, [Dan], and [Josh] ...".
    """

    return [right for right in tok.rights if
            right.dep_ == "conj" and (not allowed_pos or right.pos_ in allowed_pos)]


def get_subjects_of_verbs(verbs: List[Predicate]):
    """
    Adapted from 'get_subjects_of_verb' from textacy.

    Return all subjects of a list of verbs according to the dependency parse.
    """
    subjs = []
    for verb in verbs:
        subjs.extend(textacy.spacier.utils.get_subjects_of_verb(verb.token))
    return subjs
