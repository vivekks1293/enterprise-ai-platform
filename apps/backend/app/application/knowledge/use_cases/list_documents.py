from app.application.knowledge.dto.list_documents import (
    DocumentSummary,
    ListDocumentsRequest,
    ListDocumentsResponse,
)
from app.domain.knowledge.repositories.document_repository import (
    DocumentRepository,
)


class ListDocumentsUseCase:
    """
    Retrieves documents owned by the authenticated user.
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
    ) -> None:
        self._document_repository = document_repository

    async def execute(
        self,
        request: ListDocumentsRequest,
    ) -> ListDocumentsResponse:

        documents = await self._document_repository.list_by_owner(
            request.owner_id
        )

        summaries = [
            DocumentSummary(
                id=document.id,
                filename=document.original_filename,
                content_type=document.content_type,
                size_bytes=document.size_bytes,
                status=document.status.value,
                created_at=document.created_at,
                updated_at=document.updated_at,
            )
            for document in documents
        ]

        return ListDocumentsResponse(
            documents=summaries
        )