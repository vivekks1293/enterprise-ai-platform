from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.application.common.ports.unit_of_work import UnitOfWork
from app.application.knowledge.dto.upload_document import (
    UploadDocumentRequest,
    UploadDocumentResponse,
)
from app.application.knowledge.ports.file_storage import FileStorage
from app.domain.knowledge.entities.document import Document
from app.domain.knowledge.enums.document_status import DocumentStatus
from app.domain.knowledge.repositories.document_repository import (
    DocumentRepository,
)


class UploadDocumentUseCase:
    """
    Handles the document upload workflow.

    Coordinates metadata persistence and physical file storage
    without depending on a specific database or storage provider.
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        file_storage: FileStorage,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._document_repository = document_repository
        self._file_storage = file_storage
        self._unit_of_work = unit_of_work

    async def execute(
        self,
        request: UploadDocumentRequest,
    ) -> UploadDocumentResponse:

        self._validate_request(request)

        document_id = uuid4()
        now = datetime.now(timezone.utc)

        storage_key = self._build_storage_key(
            owner_id=request.owner_id,
            document_id=document_id,
            filename=request.filename,
        )

        document = Document(
            id=document_id,
            owner_id=request.owner_id,
            original_filename=request.filename,
            content_type=request.content_type,
            size_bytes=request.size_bytes,
            storage_key=storage_key,
            status=DocumentStatus.UPLOADING,
            created_at=now,
            updated_at=now,
        )

        await self._document_repository.create(document)
        await self._unit_of_work.commit()

        try:
            await self._file_storage.save(
                storage_key=storage_key,
                content=request.content,
            )

        except Exception:
            document.mark_failed()

            await self._document_repository.update(document)
            await self._unit_of_work.commit()

            raise

        document.mark_available()

        await self._document_repository.update(document)
        await self._unit_of_work.commit()

        return UploadDocumentResponse(
            id=document.id,
            filename=document.original_filename,
            content_type=document.content_type,
            size_bytes=document.size_bytes,
            status=document.status.value,
            created_at=document.created_at,
        )

    @staticmethod
    def _validate_request(
        request: UploadDocumentRequest,
    ) -> None:

        if not request.filename.strip():
            raise ValueError("Document filename cannot be empty.")

        if request.size_bytes <= 0:
            raise ValueError("Document size must be greater than zero.")

        if not request.content_type.strip():
            raise ValueError("Document content type cannot be empty.")

    @staticmethod
    def _build_storage_key(
        *,
        owner_id,
        document_id,
        filename: str,
    ) -> str:

        suffix = Path(filename).suffix.lower()

        return f"{owner_id}/{document_id}{suffix}"