from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from typing import Any

from pydantic import BaseModel


class UploadDocumentResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    status: str
    created_at: datetime


class DocumentSummaryResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    status: str
    created_at: datetime
    updated_at: datetime

class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    status: str
    created_at: datetime
    updated_at: datetime


class ParsedDocumentSectionResponse(BaseModel):
    content: str
    metadata: dict[str, Any]


class ParsedDocumentResponse(BaseModel):
    sections: list[ParsedDocumentSectionResponse]
    metadata: dict[str, Any]


class IngestDocumentResponse(BaseModel):
    document_id: UUID
    status: str
    parsed_document: ParsedDocumentResponse

class IndexDocumentResponse(BaseModel):
    """
    Response returned after indexing completes.
    """

    document_id: UUID

    status: str

    chunk_count: int