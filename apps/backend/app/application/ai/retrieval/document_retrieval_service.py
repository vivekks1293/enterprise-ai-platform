from uuid import UUID

from app.application.knowledge.ports.embedding_provider import (
    EmbeddingProvider,
)
from app.application.knowledge.ports.vector_store import (
    VectorStore,
)
from app.application.knowledge.ports.keyword_store import KeywordStore
from app.application.knowledge.ports.reranker import Reranker
from app.application.knowledge.contracts.vector_search_filter import (
    VectorSearchFilter,
)
from app.application.knowledge.contracts.vector_search_result import (
    VectorSearchResult,
)
from app.application.knowledge.contracts.retrieved_chunk import RetrievedChunk

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
        reranker: Reranker | None = None,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._keyword_store = keyword_store
        self._reranker = reranker

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
        elif retrieval_mode == "hybrid":
            candidate_k = max(
                resolved_top_k,
                settings.knowledge_hybrid_candidate_k,
            )
            embedding = await self._embedding_provider.embed_query(query)
            semantic_result = await self._vector_store.search(
                embedding=embedding,
                filter=search_filter,
                top_k=candidate_k,
            )
            keyword_result = await self._keyword_store.search(
                query=query,
                filter=search_filter,
                top_k=candidate_k,
            )
            result = self._fuse_with_rrf(
                semantic_result=semantic_result,
                keyword_result=keyword_result,
                top_k=max(resolved_top_k, settings.knowledge_rerank_top_k),
                rank_constant=settings.knowledge_hybrid_rrf_rank_constant,
            )
        else:
            raise ValueError(
                "retrieval_mode must be 'semantic', 'keyword', or 'hybrid'."
            )

        if self._reranker is not None and settings.knowledge_rerank_enabled:
            rerank_top_k = min(len(result.chunks), settings.knowledge_rerank_top_k)
            if rerank_top_k > 0:
                result = self._reranker.rerank(
                    query=query,
                    chunks=result.chunks[:rerank_top_k],
                    top_k=resolved_top_k,
                )

        RetrievalLogger.log(
            query=query,
            result=result,
        )

        return result

    @staticmethod
    def _fuse_with_rrf(
        *,
        semantic_result: VectorSearchResult,
        keyword_result: VectorSearchResult,
        top_k: int,
        rank_constant: int,
    ) -> VectorSearchResult:
        """Combines independent rankings without comparing their raw scores."""
        if top_k <= 0:
            return VectorSearchResult(chunks=[])

        fused_scores: dict[tuple[str, str], float] = {}
        chunks_by_key: dict[tuple[str, str], RetrievedChunk] = {}

        for search_result in (semantic_result, keyword_result):
            for rank, chunk in enumerate(search_result.chunks, start=1):
                key = (
                    str(chunk.metadata.document_id),
                    chunk.metadata.chunk_id,
                )
                fused_scores[key] = fused_scores.get(key, 0.0) + (
                    1.0 / (rank_constant + rank)
                )
                chunks_by_key.setdefault(key, chunk)

        ranked_keys = sorted(
            fused_scores,
            key=lambda key: fused_scores[key],
            reverse=True,
        )[:top_k]
        return VectorSearchResult(
            chunks=[
                RetrievedChunk(
                    content=chunks_by_key[key].content,
                    metadata=chunks_by_key[key].metadata,
                    score=fused_scores[key],
                )
                for key in ranked_keys
            ]
        )
