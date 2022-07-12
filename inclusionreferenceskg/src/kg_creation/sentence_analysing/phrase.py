import dataclasses
import uuid
from typing import List, Union, Optional

import spacy.tokens

from inclusionreferenceskg.src.reference import Reference


@dataclasses.dataclass
class Phrase:
    """
    A Phrase represents a construct of agent, predicate and patient.
    This is similar to a simple grammatical sentence consisting of subject predicate and object.
    We expand upon and generalise this concept with a Phrase. The subject is replaced by the agent and the
    object is replaced with the patient. This is done to retain the same structure between sentences
    written in the active and the passive voice. E.g., "The cat is eaten by the dog." is normalized
    so that the dog is the agent of the phrase as opposed to the object of the sentence. Further, the patient
    of a Phrase may be another Phrase as os the case for the first phrase in the sentence "The human shall ensure
    that the dog eats the cat".
    """
    patient: Union[List["PhraseObject"], "Phrase"] = dataclasses.field(default_factory=list)
    agent: List["PhraseObject"] = dataclasses.field(default_factory=list)
    predicate: List["Predicate"] = dataclasses.field(default_factory=list)

    def pprint(self, depth=0) -> str:
        print([type(p) for p in self.patient])
        new_line = "\n"

        return f"Phrase:\n" \
               f"Agent:\n{new_line.join(a.token.text for a in self.agent)}" \
               f"Predicate: {', '.join(p.token.text for p in self.predicate)}; " \
               f"Patient: {', '.join(p.token.text if type(p) == PhraseObject else p.pprint(depth=depth+1) for p in self.patient)}"


@dataclasses.dataclass
class Predicate:
    token: spacy.tokens.Token
    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))


@dataclasses.dataclass
class PhraseObject:
    """
    Effectively a wrapper for a Spacy token.
    """
    token: spacy.tokens.Token
    reference: Optional[Reference] = None
    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))
