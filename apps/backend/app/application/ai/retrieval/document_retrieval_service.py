import logging
from time import perf_counter
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
from app.application.common.ports.metrics_recorder import (
    MetricsRecorder,
    NullMetricsRecorder,
)

from app.core.config.settings import settings
from app.core.logging.logger import log_event
from app.core.telemetry.opentelemetry import mark_span_error, tracer
from app.application.ai.services.retrieval_logger import (
    RetrievalLogger,
)


logger = logging.getLogger(__name__)


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
        metrics: MetricsRecorder | None = None,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._keyword_store = keyword_store
        self._reranker = reranker
        self._metrics = metrics or NullMetricsRecorder()

    async def retrieve(
        self,
        *,
        query: str,
        owner_id: UUID,
        top_k: int | None = None,
        retrieval_mode: str = "semantic",
    ) -> VectorSearchResult:
        started_at = perf_counter()
        search_filter = VectorSearchFilter(owner_id=owner_id)
        resolved_top_k = (
            top_k
            if top_k is not None
            else settings.knowledge_retrieval_top_k
        )

        try:
            with tracer.start_as_current_span("rag.retrieval") as retrieval_span:
                retrieval_span.set_attribute("retrieval.mode", retrieval_mode)
                retrieval_span.set_attribute("retrieval.top_k", resolved_top_k)

                if retrieval_mode == "semantic":
                    with tracer.start_as_current_span(
                        "rag.retrieval.semantic"
                    ) as semantic_span:
                        stage_started_at = perf_counter()
                        embedding = await self._embedding_provider.embed_query(query)
                        result = await self._vector_store.search(
                            embedding=embedding,
                            filter=search_filter,
                            top_k=resolved_top_k,
                        )
                        stage_duration_ms = self._duration_ms(stage_started_at)
                        semantic_span.set_attributes(
                            {
                                "retrieval.result_count": len(result.chunks),
                                "retrieval.top_k": resolved_top_k,
                                "retrieval.duration_ms": stage_duration_ms,
                            }
                        )
                        self._log_search_completed(
                            event="retrieval.semantic_search.completed",
                            retrieval_mode=retrieval_mode,
                            top_k=resolved_top_k,
                            result_count=len(result.chunks),
                            duration_ms=stage_duration_ms,
                        )
                        self._metrics.observe(
                            "rag_retrieval_duration_ms",
                            stage_duration_ms,
                            labels={"retrieval_mode": retrieval_mode},
                        )
                elif retrieval_mode == "keyword":
                    with tracer.start_as_current_span(
                        "rag.retrieval.keyword"
                    ) as keyword_span:
                        stage_started_at = perf_counter()
                        result = await self._keyword_store.search(
                            query=query,
                            filter=search_filter,
                            top_k=resolved_top_k,
                        )
                        stage_duration_ms = self._duration_ms(stage_started_at)
                        keyword_span.set_attributes(
                            {
                                "retrieval.result_count": len(result.chunks),
                                "retrieval.top_k": resolved_top_k,
                                "retrieval.duration_ms": stage_duration_ms,
                            }
                        )
                        self._log_search_completed(
                            event="retrieval.keyword_search.completed",
                            retrieval_mode=retrieval_mode,
                            top_k=resolved_top_k,
                            result_count=len(result.chunks),
                            duration_ms=stage_duration_ms,
                        )
                        self._metrics.observe(
                            "rag_retrieval_duration_ms",
                            stage_duration_ms,
                            labels={"retrieval_mode": retrieval_mode},
                        )
                elif retrieval_mode == "hybrid":
                    candidate_k = max(
                        resolved_top_k,
                        settings.knowledge_hybrid_candidate_k,
                    )
                    with tracer.start_as_current_span(
                        "rag.retrieval.semantic"
                    ) as semantic_span:
                        semantic_started_at = perf_counter()
                        embedding = await self._embedding_provider.embed_query(query)
                        semantic_result = await self._vector_store.search(
                            embedding=embedding,
                            filter=search_filter,
                            top_k=candidate_k,
                        )
                        semantic_duration_ms = self._duration_ms(semantic_started_at)
                        semantic_span.set_attributes(
                            {
                                "retrieval.result_count": len(semantic_result.chunks),
                                "retrieval.top_k": candidate_k,
                                "retrieval.duration_ms": semantic_duration_ms,
                            }
                        )
                        self._log_search_completed(
                            event="retrieval.semantic_search.completed",
                            retrieval_mode=retrieval_mode,
                            top_k=candidate_k,
                            result_count=len(semantic_result.chunks),
                            duration_ms=semantic_duration_ms,
                        )
                    with tracer.start_as_current_span(
                        "rag.retrieval.keyword"
                    ) as keyword_span:
                        keyword_started_at = perf_counter()
                        keyword_result = await self._keyword_store.search(
                            query=query,
                            filter=search_filter,
                            top_k=candidate_k,
                        )
                        keyword_duration_ms = self._duration_ms(keyword_started_at)
                        keyword_span.set_attributes(
                            {
                                "retrieval.result_count": len(keyword_result.chunks),
                                "retrieval.top_k": candidate_k,
                                "retrieval.duration_ms": keyword_duration_ms,
                            }
                        )
                        self._log_search_completed(
                            event="retrieval.keyword_search.completed",
                            retrieval_mode=retrieval_mode,
                            top_k=candidate_k,
                            result_count=len(keyword_result.chunks),
                            duration_ms=keyword_duration_ms,
                        )
                    with tracer.start_as_current_span(
                        "rag.retrieval.hybrid_rrf"
                    ) as fusion_span:
                        fusion_started_at = perf_counter()
                        result = self._fuse_with_rrf(
                            semantic_result=semantic_result,
                            keyword_result=keyword_result,
                            top_k=max(resolved_top_k, settings.knowledge_rerank_top_k),
                            rank_constant=settings.knowledge_hybrid_rrf_rank_constant,
                        )
                        fusion_duration_ms = self._duration_ms(fusion_started_at)
                        fusion_span.set_attributes(
                            {
                                "retrieval.semantic_candidate_count": len(semantic_result.chunks),
                                "retrieval.keyword_candidate_count": len(keyword_result.chunks),
                                "retrieval.fused_candidate_count": len(result.chunks),
                                "retrieval.duration_ms": fusion_duration_ms,
                            }
                        )
                        log_event(
                            logger,
                            "retrieval.hybrid_rrf.completed",
                            stage="hybrid_rrf",
                            retrieval_mode=retrieval_mode,
                            semantic_candidate_count=len(semantic_result.chunks),
                            keyword_candidate_count=len(keyword_result.chunks),
                            fused_candidate_count=len(result.chunks),
                            duration_ms=fusion_duration_ms,
                        )
                    retrieval_duration_ms = self._duration_ms(started_at)
                    self._metrics.observe(
                        "rag_retrieval_duration_ms",
                        retrieval_duration_ms,
                        labels={"retrieval_mode": retrieval_mode},
                    )
                    self._metrics.observe(
                        "rag_hybrid_semantic_candidates",
                        len(semantic_result.chunks),
                        labels={"retrieval_mode": retrieval_mode},
                    )
                    self._metrics.observe(
                        "rag_hybrid_keyword_candidates",
                        len(keyword_result.chunks),
                        labels={"retrieval_mode": retrieval_mode},
                    )
                    self._metrics.observe(
                        "rag_hybrid_fused_candidates",
                        len(result.chunks),
                        labels={"retrieval_mode": retrieval_mode},
                    )
                else:
                    raise ValueError(
                        "retrieval_mode must be 'semantic', 'keyword', or 'hybrid'."
                    )

                candidate_count = len(result.chunks)

                if self._reranker is not None and settings.knowledge_rerank_enabled:
                    rerank_top_k = min(len(result.chunks), settings.knowledge_rerank_top_k)
                    if rerank_top_k > 0:
                        with tracer.start_as_current_span("rag.reranking") as rerank_span:
                            rerank_started_at = perf_counter()
                            result = self._reranker.rerank(
                                query=query,
                                chunks=result.chunks[:rerank_top_k],
                                top_k=resolved_top_k,
                            )
                            rerank_duration_ms = self._duration_ms(rerank_started_at)
                            rerank_span.set_attributes(
                                {
                                    "reranker.input_count": rerank_top_k,
                                    "reranker.output_count": len(result.chunks),
                                    "reranker.type": type(self._reranker).__name__,
                                    "reranker.duration_ms": rerank_duration_ms,
                                }
                            )
                            log_event(
                                logger,
                                "retrieval.reranking.completed",
                                stage="reranking",
                                reranker_type=type(self._reranker).__name__,
                                input_count=rerank_top_k,
                                output_count=len(result.chunks),
                                duration_ms=rerank_duration_ms,
                            )
                            self._metrics.observe(
                                "rag_reranking_duration_ms",
                                rerank_duration_ms,
                                labels={
                                    "reranker_type": type(self._reranker).__name__,
                                },
                            )

                retrieval_duration_ms = self._duration_ms(started_at)
                retrieval_span.set_attributes(
                    {
                        "retrieval.result_count": len(result.chunks),
                        "retrieval.duration_ms": retrieval_duration_ms,
                    }
                )

                self._metrics.observe(
                    "rag_retrieval_candidates",
                    candidate_count,
                    labels={"retrieval_mode": retrieval_mode},
                )
                self._metrics.observe(
                    "rag_retrieval_results",
                    len(result.chunks),
                    labels={"retrieval_mode": retrieval_mode},
                )

                RetrievalLogger.log(
                    query=query,
                    result=result,
                    retrieval_mode=retrieval_mode,
                    candidate_count=candidate_count,
                    top_k=resolved_top_k,
                    duration_ms=retrieval_duration_ms,
                )

                return result
        except Exception as exc:
            if "retrieval_span" in locals():
                mark_span_error(retrieval_span, exc)
            log_event(
                logger,
                "rag.retrieval.failed",
                stage="retrieval",
                retrieval_mode=retrieval_mode,
                exception_type=type(exc).__name__,
                duration_ms=self._duration_ms(started_at),
            )
            raise

    @staticmethod
    def _duration_ms(started_at: float) -> float:
        return round((perf_counter() - started_at) * 1000, 2)

    @staticmethod
    def _log_search_completed(
        *,
        event: str,
        retrieval_mode: str,
        top_k: int,
        result_count: int,
        duration_ms: float,
    ) -> None:
        log_event(
            logger,
            event,
            stage="retrieval",
            retrieval_mode=retrieval_mode,
            top_k=top_k,
            result_count=result_count,
            duration_ms=duration_ms,
        )

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
