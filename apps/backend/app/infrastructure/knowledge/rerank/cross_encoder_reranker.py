import math
import re

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
    """Cross-encoder reranker with term-grounded score calibration."""

    _TOKEN_PATTERN = re.compile(r"\b\w+\b", re.UNICODE)
    _STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "as", "at", "be", "because", "been", "before", "being", "below",
        "between", "both", "but", "by", "can", "could", "did", "do", "does", "doing",
        "down", "during", "each", "few", "for", "from", "further", "had", "has", "have",
        "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how",
        "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me", "more",
        "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once",
        "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same",
        "she", "should", "so", "some", "such", "than", "that", "the", "their", "theirs",
        "them", "themselves", "then", "there", "these", "they", "this", "those", "through",
        "to", "too", "under", "until", "up", "very", "was", "we", "were", "what", "when",
        "where", "which", "while", "who", "whom", "why", "with", "would", "you", "your",
        "yours", "yourself", "yourselves", "ok", "okay", "tell", "please",
    }

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
        raw_predictions = model.predict(
            pairs,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        raw_scores = (
            raw_predictions.tolist()
            if hasattr(raw_predictions, "tolist")
            else list(raw_predictions)
        )

        tokens = [t.lower() for t in self._TOKEN_PATTERN.findall(query) if t]
        content_tokens = [t for t in tokens if t not in self._STOPWORDS]
        has_content_tokens = bool(content_tokens)
        query_terms = set(content_tokens if has_content_tokens else tokens)

        scored_chunks: list[tuple[float, RetrievedChunk]] = []
        is_ms_marco = "ms-marco" in self._model_name.lower()
        for raw_score, chunk in zip(raw_scores, chunks, strict=True):
            z = float(raw_score)
            if is_ms_marco or z < 0.0 or z > 1.0:
                cross_prob = 1.0 / (1.0 + math.exp(-(z + 2.5) / 1.5))
            else:
                cross_prob = z

            chunk_tokens = set(
                t.lower()
                for t in self._TOKEN_PATTERN.findall(chunk.content)
                if t
            )
            matched_terms = query_terms & chunk_tokens
            overlap_ratio = (
                len(matched_terms) / len(query_terms) if query_terms else 1.0
            )

            if has_content_tokens and overlap_ratio == 0.0:
                final_score = min(0.35, cross_prob * 0.20)
            elif has_content_tokens:
                base_score = float(chunk.score) if chunk.score is not None else 0.0
                final_score = (
                    0.60 * cross_prob
                    + 0.35 * overlap_ratio
                    + min(0.05, max(0.0, base_score))
                )
            else:
                final_score = cross_prob

            final_score = round(min(0.98, max(0.0, final_score)), 4)
            scored_chunks.append((final_score, chunk))

        ordered = sorted(scored_chunks, key=lambda item: item[0], reverse=True)

        return VectorSearchResult(
            chunks=[
                RetrievedChunk(
                    content=chunk.content,
                    metadata=chunk.metadata,
                    score=score,
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
