from typing import List, Optional

from spacy.tokens import Span

from inclusionreferenceskg.src.document_parsing.node.node import Node
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase import Predicate, Phrase, PhraseObject
from inclusionreferenceskg.src.kg_creation.sentence_analysing.util import get_main_verbs_of_sent, get_subjects_of_verbs, \
    get_objects_of_predicate_consider_preposition


class PhraseExtractor:

    def extract_from_sentence(self, sent: Span, node: Optional[Node] = None) -> List[Phrase]:
        """
        Extracts the phrases from a sentence.

        :param sent: THe sentence to be checked for nodes.
        :param node: Optionally add the node from which the sentence originates from.
        :return:
        """

        main_verbs_of_sent = get_main_verbs_of_sent(sent)

        phrases: List[Phrase] = [Phrase(predicate=[Predicate(token=verb) for verb in verb_group]) for verb_group in
                                 main_verbs_of_sent]

        # print("START OF SENTENCE")
        # print(sent)
        # print(main_verbs_of_sent)

        # TODO subjects missing compunds
        # TODO Verbs missing negations, auxilaries

        # used to mark phrases for deletion
        deletion_marks = set()

        for phrase in phrases:
            is_passive = phrase.predicate[0].token.tag_ == "VBN"
            phrase.agent_objects = [PhraseObject(tok) for tok in get_subjects_of_verbs(phrase.predicate)]

            verb_as_patient = [tok for pred in phrase.predicate for tok in pred.token.children if
                               tok.dep_ in {"ccomp", "advcl"}]

            phrase_as_patient = []
            for vap in verb_as_patient:
                for p in phrases:
                    for pred in p.predicate:
                        if pred.token == vap:
                            phrase_as_patient.append(p)
                            deletion_marks.add(p.id)
                            break

            """if phrase_as_patient and is_passive:
                print(sent)
                phrase.pprint()
                displacy.serve(sent, "dep")
                raise Exception("Phrase as a patient cannot coincide with a passive voice.")"""

            grammatical_object = get_objects_of_predicate_consider_preposition(phrase.predicate)

            phrase.patient_phrases = phrase_as_patient
            phrase.patient_objects = [PhraseObject(token=tok) for tok in grammatical_object]

            if is_passive:
                # Is this really necessary?
                phrase.patient_objects, phrase.agent_objects = phrase.agent_objects, phrase.patient_objects
                phrase.patient_phrases, phrase.agent_phrases = phrase.agent_phrases, phrase.patient_phrases

            phrase.patient_phrases, phrase.condition_phrases = [x for x in phrase.patient_phrases if
                                                                not self.is_conditional(x)], [x for x in
                                                                                              phrase.patient_phrases if
                                                                                              self.is_conditional(x)]

        phrases = [phrase for phrase in phrases if phrase.id not in deletion_marks]

        for phrase in phrases:
            # We only add the node id to the top level phrases.
            if node:
                phrase.origin_node_id = node.id

        return phrases

    def is_conditional(self, phrase: Phrase):
        """
        Primitive heuristic to determine if a phrase is a conditional.

        :param phrase:
        """
        # TODO CHeck completeness of {"IN", "WRB"}
        return any(tok.tag_ in {"IN", "WRB"} for pred in phrase.predicate for tok in pred.token.children)
