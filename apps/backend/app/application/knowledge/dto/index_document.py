from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class IndexDocumentRequest:
    owner_id: UUID
    document_id: UUID


@dataclass(frozen=True)
class IndexDocumentResponse:
    document_id: UUID
    status: str
    chunk_count: int