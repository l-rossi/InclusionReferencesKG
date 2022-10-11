from __future__ import annotations

import dataclasses
import uuid
from typing import List, Optional, Set

import spacy.tokens


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
    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))

    agent_objects: List[PhraseObject] = dataclasses.field(default_factory=list)
    agent_phrases: List[Phrase] = dataclasses.field(default_factory=list)

    patient_objects: List[PhraseObject] = dataclasses.field(default_factory=list)
    patient_phrases: List[Phrase] = dataclasses.field(default_factory=list)

    predicate: List[Predicate] = dataclasses.field(default_factory=list)

    condition_phrases: List[Phrase] = dataclasses.field(default_factory=list)

    def pprint(self, depth=0, visited: Set[str] = None):
        """
        Prints the phrase in a human readable form.

        :param depth: Indicates the current indent.
        :param visited: Leeps track of which phrases have been visited to avoid recursion errors.
        """
        if visited is None:
            visited = set()

        self_visited = self.id in visited
        visited.add(self.id)

        indent = "    " * depth

        print(f"{indent}Phrase{{")
        print(f"{indent}  Agent:")
        if self_visited:
            print(f"{indent}    ...")
        else:
            for p in self.agent_objects:
                print(f"{indent}    {p.pretty_str()}")

            for p in self.agent_phrases:
                p.pprint(depth=depth + 1, visited=visited)

        print(f"{indent}  Predicate:")
        for p in self.predicate:
            print(f"{indent}    {p.token} {p.token.lemma_} {p.token.tag_}")

            print(f"{indent}  Patient:")
        if self_visited:
            print(f"{indent}    ...")
        else:
            for p in self.patient_objects:
                print(f"{indent}    {p.pretty_str()}")

            for p in self.patient_phrases:
                p.pprint(depth=depth + 1, visited=visited)

        print(f"{indent}  Conditions:")
        if self_visited:
            print(f"{indent}    ...")
        else:
            for p in self.condition_phrases:
                p.pprint(depth=depth + 1, visited=visited)

        print(f"{indent}}}")


@dataclasses.dataclass
class Predicate:
    """
    Used either in a phrase or as the item of a Process Entity.
    """
    token: spacy.tokens.Token
    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))


@dataclasses.dataclass
class PhraseObject:
    """
    Effectively a wrapper for a Spacy token.

    Used either in a phrase or as the item of an Object Entity.
    """
    token: spacy.tokens.Token
    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))

    # Extensions. These attributes are not part of the main knowledge graph creation methods but are rather
    # extensions as described by the evaluation section of the paper.
    described_by: List[Phrase] = dataclasses.field(default_factory=list)
    possessors: List[PhraseObject] = dataclasses.field(default_factory=list)

    def pretty_str(self) -> str:
        coref_chain = self.token.doc._.coref_chains.resolve(self.token)
        coref_str = ""
        if coref_chain and self.token.pos_ == "PRON":
            coref_str = f", Coreferences: {coref_chain}"

        return f"{self._proper_noun_str()}{coref_str}"

    def _proper_noun_str(self):
        for chunk in self.token.doc.noun_chunks:
            if self.token in chunk:
                return chunk.text

        return " ".join(x.text for x in
                        sorted((self.token,) + tuple(tok for tok in self.token.children if tok.dep_ == "compound"),
                               key=lambda x: x.i))
