from app.application.knowledge.dto.get_document import (
    GetDocumentRequest,
    GetDocumentResponse,
)
from app.application.knowledge.exceptions import (
    DocumentNotFoundError,
)
from app.domain.knowledge.repositories.document_repository import (
    DocumentRepository,
)


class GetDocumentUseCase:
    """
    Retrieves document metadata for the authenticated owner.
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
    ) -> None:
        self._document_repository = document_repository

    async def execute(
        self,
        request: GetDocumentRequest,
    ) -> GetDocumentResponse:

        document = await self._document_repository.get_by_id(
            document_id=request.document_id,
            owner_id=request.owner_id,
        )

        if document is None:
            raise DocumentNotFoundError()

        return GetDocumentResponse(
            id=document.id,
            filename=document.original_filename,
            content_type=document.content_type,
            size_bytes=document.size_bytes,
            status=document.status.value,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )