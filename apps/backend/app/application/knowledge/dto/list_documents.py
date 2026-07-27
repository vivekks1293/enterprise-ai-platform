from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ListDocumentsRequest:
    owner_id: UUID


@dataclass(frozen=True)
class DocumentSummary:
    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ListDocumentsResponse:
    documents: list[DocumentSummary]