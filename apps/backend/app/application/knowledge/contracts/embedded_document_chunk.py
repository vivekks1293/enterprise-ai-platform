from dataclasses import dataclass

from app.application.knowledge.contracts.document_chunk import (
    DocumentChunk,
)
from app.application.knowledge.contracts.embedding_vector import (
    EmbeddingVector,
)


@dataclass(frozen=True)
class EmbeddedDocumentChunk:
    """
    A chunk together with its embedding.
    """

    chunk: DocumentChunk

    embedding: EmbeddingVector