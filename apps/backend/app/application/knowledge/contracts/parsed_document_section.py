from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ParsedDocumentSection:
    """
    Represents a logical section extracted from a document.

    A section may correspond to a PDF page, DOCX section,
    or a complete text-based document.
    """

    content: str

    metadata: dict[str, Any]