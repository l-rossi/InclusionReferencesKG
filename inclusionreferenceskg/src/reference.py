from dataclasses import dataclass, field
from typing import List, Optional

from inclusionreferenceskg.src.document_parsing.node.node import Node


@dataclass
class Reference:
    """
    Class for capturing information on references.
    """

    start: int
    text_content: str
    reference_qualifier: List[List[Node]] = field(default_factory=list)
