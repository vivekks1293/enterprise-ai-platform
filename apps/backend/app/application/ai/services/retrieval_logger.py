import logging

from app.application.knowledge.contracts.vector_search_result import (
    VectorSearchResult,
)

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
    ) -> None:

        logger.info("=" * 80)
        logger.info("RETRIEVAL")
        logger.info("=" * 80)

        logger.info("Query:")
        logger.info(query)

        logger.info("Retrieved Chunks: %s", len(result.chunks))

        for index, chunk in enumerate(result.chunks, start=1):

            logger.info(
                "[%s] %s | Chunk=%s | Score=%.3f",
                index,
                chunk.metadata.filename,
                chunk.metadata.chunk_index,
                chunk.similarity_score,
            )

        logger.info("=" * 80)