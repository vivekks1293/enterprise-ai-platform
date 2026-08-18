import math
import logging
from time import perf_counter

from app.application.knowledge.contracts.retrieved_chunk import (
    RetrievedChunk,
)
from app.core.logging.logger import log_event


logger = logging.getLogger(__name__)


class ContextAssembler:
    """
    Selects ranked retrieved chunks for LLM context.

    Token usage is estimated as four thirds of the whitespace-delimited word
    count. This is intentionally an approximation, not model tokenization.
    """

    def __init__(self, max_tokens: int) -> None:
        if max_tokens < 0:
            raise ValueError("max_tokens must not be negative.")

        self._max_tokens = max_tokens

    def assemble(
        self,
        retrieved_chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        """Returns deduplicated whole chunks that fit the configured budget."""

        started_at = perf_counter()
        selected_chunks: list[RetrievedChunk] = []
        seen_chunk_ids: set[str] = set()
        used_tokens = 0
        duplicate_count = 0

        for chunk in retrieved_chunks:
            chunk_id = chunk.metadata.chunk_id
            if chunk_id in seen_chunk_ids:
                duplicate_count += 1
                continue

            seen_chunk_ids.add(chunk_id)
            estimated_tokens = self._estimate_tokens(chunk.content)

            if used_tokens + estimated_tokens > self._max_tokens:
                break

            selected_chunks.append(chunk)
            used_tokens += estimated_tokens

        log_event(
            logger,
            "context.assembled",
            stage="context",
            candidate_count=len(retrieved_chunks),
            selected_count=len(selected_chunks),
            estimated_tokens=used_tokens,
            duplicate_count=duplicate_count,
            duration_ms=round((perf_counter() - started_at) * 1000, 2),
        )
        return selected_chunks

    @staticmethod
    def _estimate_tokens(content: str) -> int:
        """Estimates tokens from whitespace-delimited words for budget control."""

        return math.ceil(len(content.split()) / 0.75)