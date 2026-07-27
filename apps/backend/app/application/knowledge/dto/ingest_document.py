from dataclasses import dataclass
from uuid import UUID

from app.application.knowledge.contracts.parsed_document import (
    ParsedDocument,
)


@dataclass(frozen=True)
class IngestDocumentRequest:
    owner_id: UUID
    document_id: UUID


@dataclass(frozen=True)
class IngestDocumentResponse:
    document_id: UUID
    status: str
    parsed_document: ParsedDocument