from __future__ import annotations

from app.application.knowledge.contracts.retrieved_chunk import (
    RetrievedChunk,
)
from app.application.knowledge.contracts.vector_search_result import (
    VectorSearchResult,
)
from app.application.knowledge.ports.reranker import Reranker
from app.core.config.settings import settings
from app.infrastructure.knowledge.rerank.simple_reranker import (
    SimpleReranker,
)


class CrossEncoderReranker(Reranker):
    """Cross-encoder reranker using sentence-transformers."""

    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or settings.knowledge_rerank_model
        self._model = None

    def rerank(
        self,
        *,
        query: str,
        chunks: list[RetrievedChunk],
        top_k: int,
    ) -> VectorSearchResult:
        if top_k <= 0 or not chunks:
            return VectorSearchResult(chunks=[])

        model = self._get_model()
        if model is None:
            return SimpleReranker().rerank(
                query=query,
                chunks=chunks,
                top_k=top_k,
            )

        pairs = [(query, chunk.content) for chunk in chunks]
        scores = model.predict(
            pairs,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        score_items = list(zip(scores.tolist() if hasattr(scores, "tolist") else list(scores), chunks, strict=True))
        ordered = sorted(score_items, key=lambda item: float(item[0]), reverse=True)

        return VectorSearchResult(
            chunks=[
                RetrievedChunk(
                    content=chunk.content,
                    metadata=chunk.metadata,
                    score=float(score),
                )
                for score, chunk in ordered[:top_k]
            ]
        )

    def _get_model(self):
        if self._model is not None:
            return self._model

        try:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(self._model_name, max_length=512)
            return self._model
        except Exception:
            return None
