from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.domain.knowledge.enums.document_status import DocumentStatus


@dataclass
class Document:
    """
    Represents a document managed by the Knowledge capability.
    """

    id: UUID
    owner_id: UUID

    original_filename: str
    content_type: str
    size_bytes: int

    storage_key: str

    status: DocumentStatus

    created_at: datetime
    updated_at: datetime

    def mark_available(self) -> None:
        """
        Marks the document as successfully stored.
        """

        self.status = DocumentStatus.AVAILABLE
        self.updated_at = datetime.now(timezone.utc)

    def mark_processing(self) -> None:
        """
        Marks the document as currently being indexed.
        """

        self.status = DocumentStatus.INDEXING
        self.updated_at = datetime.now(timezone.utc)

    def mark_processed(self) -> None:
        """
        Marks the document as successfully ingested.
        """

        self.status = DocumentStatus.INDEXED
        self.updated_at = datetime.now(timezone.utc)

    def mark_failed(self) -> None:
        """
        Marks the document as failed.
        """

        self.status = DocumentStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)

    def mark_indexing(self) -> None:
        """
        Marks the document as currently being indexed.
        """
        self.status = DocumentStatus.INDEXING
        self.updated_at = datetime.now(timezone.utc)


    def mark_indexed(self) -> None:
        """
        Marks the document as successfully indexed.
        """
        self.status = DocumentStatus.INDEXED
        self.updated_at = datetime.now(timezone.utc)


    def mark_failed(self) -> None:
        """
        Marks the document as failed.
        """
        self.status = DocumentStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)