from app.application.ai.contracts.citation import Citation
from app.application.knowledge.contracts.retrieved_chunk import (
    RetrievedChunk,
)


class CitationMapper:
    """
    Converts RetrievedChunk objects into citations.
    """

    @staticmethod
    def from_retrieved_chunks(
        chunks: list[RetrievedChunk],
    ) -> list[Citation]:

        citations: list[Citation] = []

        for chunk in chunks:

            citations.append(
                Citation(
                    document_id=chunk.metadata.document_id,
                    filename=chunk.metadata.filename,
                    chunk_id=chunk.metadata.chunk_id,
                    chunk_index=chunk.metadata.chunk_index,
                    page_number=chunk.metadata.page_number,
                    distance=chunk.distance,
                )
            )

        return citations