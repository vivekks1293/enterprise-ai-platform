from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class GetDocumentRequest:
    owner_id: UUID
    document_id: UUID


@dataclass(frozen=True)
class GetDocumentResponse:
    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    status: str
    created_at: datetime
    updated_at: datetime