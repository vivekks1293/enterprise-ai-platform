from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DownloadDocumentRequest:
    owner_id: UUID
    document_id: UUID


@dataclass
class DownloadDocumentResponse:
    filename: str
    content_type: str
    content: AsyncIterator[bytes]