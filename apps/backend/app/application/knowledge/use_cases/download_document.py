from app.application.knowledge.dto.download_document import (
    DownloadDocumentRequest,
    DownloadDocumentResponse,
)
from app.application.knowledge.exceptions import (
    DocumentNotFoundError,
)
from app.application.knowledge.ports.file_storage import (
    FileStorage,
)
from app.domain.knowledge.repositories.document_repository import (
    DocumentRepository,
)


class DownloadDocumentUseCase:
    """
    Retrieves an owned document and provides its content stream.
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        file_storage: FileStorage,
    ) -> None:
        self._document_repository = document_repository
        self._file_storage = file_storage

    async def execute(
        self,
        request: DownloadDocumentRequest,
    ) -> DownloadDocumentResponse:

        document = await self._document_repository.get_by_id(
            document_id=request.document_id,
            owner_id=request.owner_id,
        )

        if document is None:
            raise DocumentNotFoundError()

        exists = await self._file_storage.exists(
            storage_key=document.storage_key,
        )

        if not exists:
            raise DocumentNotFoundError()

        content = self._file_storage.read(
            storage_key=document.storage_key,
        )

        return DownloadDocumentResponse(
            filename=document.original_filename,
            content_type=document.content_type,
            content=content,
        )