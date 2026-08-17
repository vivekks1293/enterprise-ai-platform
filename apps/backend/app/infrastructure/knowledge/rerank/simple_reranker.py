import re

from app.application.knowledge.contracts.retrieved_chunk import (
    RetrievedChunk,
)
from app.application.knowledge.contracts.vector_search_result import (
    VectorSearchResult,
)
from app.application.knowledge.ports.reranker import Reranker


class SimpleReranker(Reranker):
    """Lightweight lexical reranker using query-token overlap."""

    _TOKEN_PATTERN = re.compile(r"\b\w+\b", re.UNICODE)

    def rerank(
        self,
        *,
        query: str,
        chunks: list[RetrievedChunk],
        top_k: int,
    ) -> VectorSearchResult:
        if top_k <= 0 or not chunks:
            return VectorSearchResult(chunks=[])

        query_tokens = {
            token.lower()
            for token in self._tokenize(query)
            if token
        }

        ranked = []
        for chunk in chunks:
            overlap = 0
            if query_tokens:
                chunk_tokens = {
                    token.lower()
                    for token in self._tokenize(chunk.content)
                    if token
                }
                overlap = len(query_tokens & chunk_tokens)

            score = float(chunk.score) + (overlap * 10.0)
            ranked.append((score, chunk))

        ordered = sorted(ranked, key=lambda item: item[0], reverse=True)
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

    @classmethod
    def _tokenize(cls, value: str) -> list[str]:
        return cls._TOKEN_PATTERN.findall(value.lower())
