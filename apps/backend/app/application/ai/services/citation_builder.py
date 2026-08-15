from app.domain.ai.models.citation import Citation
from app.application.knowledge.contracts.retrieved_chunk import (
    RetrievedChunk,
)


class CitationBuilder:
    """
    Builds user-facing citations from retrieved document chunks.
    """

    @staticmethod
    def build(
        retrieved_chunks: list[RetrievedChunk],
    ) -> list[Citation]:
        """
        Converts retrieved chunks into citations.
        """

        citations: list[Citation] = []

        for index, chunk in enumerate(
            retrieved_chunks,
            start=1,
        ):
            citations.append(
                Citation(
                    citation_id=index,
                    document_id=chunk.metadata.document_id,
                    chunk_id=chunk.metadata.chunk_id,
                    filename=chunk.metadata.filename,
                    page_number=chunk.metadata.page_number,
                    similarity_score=chunk.similarity_score,
                )
            )

        return citations