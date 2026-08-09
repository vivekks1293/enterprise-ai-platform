from fastapi import Depends

from app.application.ai.use_cases.retrieve_context import (
    RetrieveContextUseCase,
)
from app.application.ai.retrieval.document_retrieval_service import (
    DocumentRetrievalService,
)
from app.core.dependencies.ai import (
    get_document_retrieval_service,
)


def get_retrieve_context_use_case(
    retrieval_service: DocumentRetrievalService = Depends(
        get_document_retrieval_service,
    ),
) -> RetrieveContextUseCase:
    """
    Provides the RetrieveContextUseCase.
    """

    return RetrieveContextUseCase(
        retrieval_service=retrieval_service,
    )