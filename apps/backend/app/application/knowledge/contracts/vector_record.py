from dataclasses import dataclass

from app.application.knowledge.contracts.document_chunk import (
    DocumentChunk,
)
from app.application.knowledge.contracts.embedding_vector import (
    EmbeddingVector,
)


@dataclass(frozen=True)
class VectorRecord:
    """
    Represents one indexed record inside
    a vector database.
    """

    chunk: DocumentChunk

    embedding: EmbeddingVector