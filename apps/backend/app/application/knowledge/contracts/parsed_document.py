from dataclasses import dataclass
from typing import Any

from app.application.knowledge.contracts.parsed_document_section import (
    ParsedDocumentSection,
)


@dataclass(frozen=True)
class ParsedDocument:
    """
    Framework-independent representation of extracted document content.
    """

    sections: list[ParsedDocumentSection]

    metadata: dict[str, Any]