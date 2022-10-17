from itertools import chain
from typing import List, Iterable, Set, Tuple

from spacy.tokens import Span, Doc

from kg_creation.sentence_analysing.phrase import Predicate, Phrase, PhraseObject
from kg_creation.sentence_analysing.util import get_main_verbs_of_sent, get_nominal_subjects_of_verbs, \
    get_objects_of_predicate_consider_preposition, is_acl_without_subj, CLAUSAL_SUBJ_DEPS, \
    CONDITIONAL_SUBORDINATE_CONJUNCTIONS


def is_conditional(phrase: Phrase):
    """
    Primitive heuristic to determine if a phrase is a conditional.

    :param phrase: The phrase to be checked for conditionality.
    """

    # examples of conditional phrases: provided that, if and to the extent that
    return any(
        tok.pos_ == "SCONJ" and tok.text in CONDITIONAL_SUBORDINATE_CONJUNCTIONS for pred in phrase.predicate for tok in
        pred.token.children)


class PhraseExtractor:
    """
    The PhraseExtractor class acts as a namespace for the 'extract_from_sentence' method and its helpers.
    It is used to extract phrase constructs, i.e., agent-predicate-patient-constructs, from a spacy span.
    """

    def extract_from_sentence(self, sent: Span) -> List[Phrase]:
        """
        Extracts the phrases from a sentence.

        :param sent: The sentence to be checked for nodes.
        :return: A list of top-level phrases extracted from the sentence.
        """

        main_verbs_of_sent = get_main_verbs_of_sent(sent)

        phrases: List[Phrase] = [Phrase(predicate=[Predicate(token=verb) for verb in verb_group]) for verb_group in
                                 main_verbs_of_sent]

        # Used to mark phrases for deletion from the top level
        # Generally, the deleted phrases will still be accessible through other phrases.
        deletion_marks = set()

        for phrase in phrases:
            phrase.agent_objects = [PhraseObject(tok) for tok in get_nominal_subjects_of_verbs(phrase.predicate)]
            grammatical_object = get_objects_of_predicate_consider_preposition(phrase.predicate)
            phrase.patient_objects = [PhraseObject(tok) for tok in grammatical_object]

            object_children = [child for obj in chain(phrase.agent_objects, phrase.patient_objects) for child in
                               obj.token.children]

            phrase.patient_phrases, phrase.agent_phrases = self._link_phrases(deletion_marks, object_children, phrase,
                                                                              phrases)

            self._switch_dependants_on_passive(phrase)
            self._resolve_relative_clauses(chain(phrase.agent_objects, phrase.patient_objects))
            phrase.patient_phrases, phrase.condition_phrases = self._split_conditional_phrases(phrase.patient_phrases)
            self._resolve_anaphoric_references(phrase)

            # Extensions
            self._extract_adnominal_clauses(chain(phrase.agent_objects, phrase.patient_objects), phrases,
                                            deletion_marks)
            self._extract_possessors(chain(phrase.agent_objects, phrase.patient_objects))
        # Remove phrases with no agent and patient from the top level.
        for phrase in phrases:
            if not phrase.agent_phrases and not phrase.agent_objects and not phrase.patient_phrases and not phrase.patient_objects:
                deletion_marks.add(phrase.id)

        phrases = [phrase for phrase in phrases if phrase.id not in deletion_marks]

        return phrases

    def _extract_possessors(self, phrase_objects: Iterable[PhraseObject]):
        """
        Extracts possessive constructs, for example 'of' and genitive cases.
        """

        # Go through all and create new Phrase Objects along the way.
        for phrase_object in phrase_objects:
            poss_stack = [phrase_object]
            while poss_stack:
                curr = poss_stack.pop()

                genitives = [PhraseObject(x) for x in curr.token.children if x.dep_ == "poss"]
                ofs = [PhraseObject(y) for x in curr.token.children if x.text == "of" for y in x.children if
                       y.dep_ == "pobj"]

                curr.possessors.extend(genitives)
                curr.possessors.extend(ofs)
                poss_stack.extend(genitives)
                poss_stack.extend(ofs)

    def _extract_adnominal_clauses(self, phrase_objects: Iterable[PhraseObject], phrases: Iterable[Phrase],
                                   deletion_marks: Set[str]):
        """
        Extracts adnominal clauses
        """
        for phrase_object in phrase_objects:
            for phrase in phrases:
                if any(p.token.head == phrase_object.token and p.token.dep_ == "acl" for p in phrase.predicate):
                    deletion_marks.add(phrase.id)
                    phrase_object.described_by.append(phrase)

    def _switch_dependants_on_passive(self, phrase):
        """
        Switches agent and patient of a phrase if the phrase is in the passive voice.
        """
        is_passive = phrase.predicate[0].token.tag_ == "VBN"
        if is_passive:
            phrase.patient_objects, phrase.agent_objects = phrase.agent_objects, phrase.patient_objects
            phrase.patient_phrases, phrase.agent_phrases = phrase.agent_phrases, phrase.patient_phrases

    def _resolve_anaphoric_references(self, phrase):
        """
        Resolves anaphoric references if possible.
        """
        if Doc.get_extension("coref_chains"):
            extend_phrase_objects_by_coref(phrase.agent_objects)
            extend_phrase_objects_by_coref(phrase.patient_objects)

    def _resolve_relative_clauses(self, phrase_objects: Iterable[PhraseObject]):
        """
        Removes relative pronouns and replaces them with their respective heads.
        """
        for po in phrase_objects:
            if po.token.head.dep_ == "relcl" and po.token.pos_ == "PRON":
                po.token = po.token.head.head

    def _split_conditional_phrases(self, phrases: Iterable[Phrase]):
        """
        Splits a list of phrases depending into conditional and regular patient phrases.
        """
        conditionals = []
        patients = []
        for x in phrases:
            if is_conditional(x):
                conditionals.append(x)
            else:
                patients.append(x)

        return patients, conditionals

    def _link_phrases(self, deletion_marks, object_children, phrase, phrases) -> Tuple[List[Phrase], List[Phrase]]:
        """
        Links phrases based on the predicate of a phrase being used like an object in another sentence.

        :return: A tuple consisting of the phrase's patient phrases and its agent phrases
        """

        verb_as_patient = [tok for pred in phrase.predicate for tok in chain(pred.token.children, object_children)
                           if tok.dep_ in {"ccomp", "advcl"} or is_acl_without_subj(tok) or (
                               tok.dep_ == "xcomp" and tok.pos_ in {"VERB", "AUX"})]

        phrase_as_patient = []
        for vap in verb_as_patient:
            for p in phrases:
                if p.id == phrase.id:
                    continue

                for pred in p.predicate:
                    if pred.token == vap:
                        phrase_as_patient.append(p)
                        deletion_marks.add(p.id)
                        break

        verb_as_agent = [tok for pred in phrase.predicate for tok in chain(pred.token.children, object_children)
                         if tok.dep_ in CLAUSAL_SUBJ_DEPS]
        phrase_as_agent = []
        for vap in verb_as_agent:
            for p in phrases:
                if p.id == phrase.id:
                    continue

                for pred in p.predicate:
                    if pred.token == vap:
                        phrase_as_agent.append(p)
                        deletion_marks.add(p.id)
                        break

        return phrase_as_patient, phrase_as_agent


def extend_phrase_objects_by_coref(phrase_objects: List[PhraseObject]):
    """
    Modifies the passed list of phrase_objects so that tokens referring to other tokens (it, they, ...)
    are added.

    Warning: This function modifies both the passed in list and the PhraseObjects within.
    """
    new_pos = []
    for po in phrase_objects:
        if res := po.token.doc._.coref_chains.resolve(po.token):
            po.token = res[0]
            for r in res[1:]:
                new_pos.append(PhraseObject(token=r))
    phrase_objects.extend(new_pos)
