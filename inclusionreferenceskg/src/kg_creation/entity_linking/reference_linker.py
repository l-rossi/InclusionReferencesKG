from spacy.tokens import Token

from inclusionreferenceskg.src.document_parsing.node.node import Node
from inclusionreferenceskg.src.reference_resolution.reference_resolver import ReferenceResolver


class ReferenceLinker:

    def __init__(self, reference_resolver: ReferenceResolver, root: Node):
        """
        :param reference_resolver: The ReferenceResolver used to resolve references.
        :param root: The root from which to resolve references
        """

        self.root = root
        self.reference_resolver = reference_resolver

    def resolve(self, token: Token):

        if token.tag_ == "REF":
            target = token._.reference_target
