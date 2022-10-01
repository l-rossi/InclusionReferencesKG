from itertools import chain
from typing import List, Optional

from spacy.tokens import Span, Doc

from document_parsing.node.node import Node
from kg_creation.sentence_analysing.phrase import Predicate, Phrase, PhraseObject
from kg_creation.sentence_analysing.util import get_main_verbs_of_sent, get_subjects_of_verbs, \
    get_objects_of_predicate_consider_preposition


def is_conditional(phrase: Phrase):
    """
    Primitive heuristic to determine if a phrase is a conditional.

    :param phrase: The phrase to be checked for conditionality.
    """

    # examples of conditional phrases: provided that, if and to the extent that
    return any(tok.pos_ == "SCONJ" for pred in phrase.predicate for tok in pred.token.children) or any(
        pred.token.dep_ == "acl" for pred in phrase.predicate)


class PhraseExtractor:

    def extract_from_sentence(self, sent: Span, node: Optional[Node] = None) -> List[Phrase]:
        """
        Extracts the phrases from a sentence.

        :param sent: The sentence to be checked for nodes.
        :param node: Optionally add the node from which the sentence originates from.
        :return:
        """

        main_verbs_of_sent = get_main_verbs_of_sent(sent)

        phrases: List[Phrase] = [Phrase(predicate=[Predicate(token=verb) for verb in verb_group]) for verb_group in
                                 main_verbs_of_sent]

        # used to mark phrases for deletion
        deletion_marks = set()

        for phrase in phrases:
            is_passive = phrase.predicate[0].token.tag_ == "VBN"
            phrase.agent_objects = [PhraseObject(tok) for tok in get_subjects_of_verbs(phrase.predicate)]

            grammatical_object = get_objects_of_predicate_consider_preposition(phrase.predicate)
            phrase.patient_objects = [PhraseObject(token=tok) for tok in grammatical_object]

            object_children = [child for obj in phrase.agent_objects + phrase.patient_objects for child in
                               obj.token.children]

            # link phrases
            verb_as_patient = [tok for pred in phrase.predicate for tok in chain(pred.token.children, object_children)
                               if
                               tok.dep_ in {"ccomp", "advcl", "acl"}]

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

            phrase.patient_phrases = phrase_as_patient

            if is_passive:
                phrase.patient_objects, phrase.agent_objects = phrase.agent_objects, phrase.patient_objects
                phrase.patient_phrases, phrase.agent_phrases = phrase.agent_phrases, phrase.patient_phrases

            phrase.patient_phrases, phrase.condition_phrases = [x for x in phrase.patient_phrases if
                                                                not is_conditional(x)], \
                                                               [x for x in phrase.patient_phrases if
                                                                is_conditional(x)]

            # resolve relative clauses
            for po in phrase.agent_objects + phrase.patient_objects:
                if po.token.head.dep_ == "relcl" and po.token.pos_ == "PRON":
                    po.token = po.token.head.head

            # resolve anaphoric references
            if Doc.get_extension("coref_chains"):
                extend_phrase_objects_by_coref(phrase.agent_objects)
                extend_phrase_objects_by_coref(phrase.patient_objects)

        # Remove phrases with no agent and patient from the top level.
        for phrase in phrases:
            if not phrase.agent_phrases and not phrase.agent_objects and not phrase.patient_phrases and not phrase.patient_objects:
                deletion_marks.add(phrase.id)

        phrases = [phrase for phrase in phrases if phrase.id not in deletion_marks]

        for phrase in phrases:
            # We only add the node id to the top level phrases.
            if node:
                phrase.origin_node_id = node.id

        return phrases


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
