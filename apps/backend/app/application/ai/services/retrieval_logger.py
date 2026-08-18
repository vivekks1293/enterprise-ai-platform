import hashlib
import logging

from app.application.knowledge.contracts.vector_search_result import (
    VectorSearchResult,
)
from app.core.logging.logger import log_event

logger = logging.getLogger(__name__)


class RetrievalLogger:
    """
    Logs retrieval diagnostics for observability.
    """

    @staticmethod
    def log(
        *,
        query: str,
        result: VectorSearchResult,
        retrieval_mode: str,
        candidate_count: int,
        top_k: int,
        duration_ms: float,
    ) -> None:
        """Logs safe retrieval metadata without query or document content."""

        log_event(
            logger,
            "retrieval.completed",
            stage="retrieval",
            retrieval_mode=retrieval_mode,
            query_length=len(query),
            query_hash=hashlib.sha256(query.encode("utf-8")).hexdigest(),
            candidate_count=candidate_count,
            result_count=len(result.chunks),
            top_k=top_k,
            duration_ms=duration_ms,
        )
