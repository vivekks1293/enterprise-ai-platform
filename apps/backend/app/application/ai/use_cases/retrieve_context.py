from app.application.ai.dto.retrieval_request import RetrievalRequest
from app.application.ai.dto.retrieval_response import (
    RetrievalResponse,
    RetrievedChunkResponse,
)
from app.application.ai.retrieval.document_retrieval_service import (
    DocumentRetrievalService,
)


class RetrieveContextUseCase:

    def __init__(
        self,
        retrieval_service: DocumentRetrievalService,
    ):
        self._retrieval_service = retrieval_service

    async def execute(
        self,
        *,
        owner_id,
        request: RetrievalRequest,
    ) -> RetrievalResponse:

        result = await self._retrieval_service.retrieve(
            query=request.query,
            owner_id=owner_id,
            top_k=request.top_k,
        )

        return RetrievalResponse(
            chunks=[
                RetrievedChunkResponse(
                    content=chunk.content,
                    score=chunk.score,
                    filename=chunk.metadata.filename,
                    chunk_index=chunk.metadata.chunk_index,
                )
                for chunk in result.chunks
            ]
        )