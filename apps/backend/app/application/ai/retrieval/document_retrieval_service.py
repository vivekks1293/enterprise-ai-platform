from uuid import UUID

from app.application.knowledge.ports.embedding_provider import (
    EmbeddingProvider,
)
from app.application.knowledge.ports.vector_store import (
    VectorStore,
)
from app.application.knowledge.ports.keyword_store import KeywordStore
from app.application.knowledge.contracts.vector_search_filter import (
    VectorSearchFilter,
)
from app.application.knowledge.contracts.vector_search_result import (
    VectorSearchResult,
)

from app.core.config.settings import settings
from app.application.ai.services.retrieval_logger import (
    RetrievalLogger,
)


class DocumentRetrievalService:
    """
    Retrieves semantically relevant document chunks.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        keyword_store: KeywordStore,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._keyword_store = keyword_store

    async def retrieve(
        self,
        *,
        query: str,
        owner_id: UUID,
        top_k: int | None = None,
        retrieval_mode: str = "semantic",
    ) -> VectorSearchResult:
        search_filter = VectorSearchFilter(owner_id=owner_id)
        resolved_top_k = (
            top_k
            if top_k is not None
            else settings.knowledge_retrieval_top_k
        )

        if retrieval_mode == "semantic":
            embedding = await self._embedding_provider.embed_query(query)
            result = await self._vector_store.search(
                embedding=embedding, filter=search_filter, top_k=resolved_top_k
            )
        elif retrieval_mode == "keyword":
            result = await self._keyword_store.search(
                query=query, filter=search_filter, top_k=resolved_top_k
            )
        else:
            raise ValueError("retrieval_mode must be 'semantic' or 'keyword'.")

        RetrievalLogger.log(
            query=query,
            result=result,
        )

        return result
