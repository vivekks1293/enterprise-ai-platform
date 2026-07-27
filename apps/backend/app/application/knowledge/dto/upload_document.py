from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass(frozen=True)
class UploadDocumentRequest:
    owner_id: UUID

    filename: str
    content_type: str
    size_bytes: int

    content: AsyncIterator[bytes]

@dataclass(frozen=True)
class UploadDocumentResponse:
    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    status: str
    created_at: datetime