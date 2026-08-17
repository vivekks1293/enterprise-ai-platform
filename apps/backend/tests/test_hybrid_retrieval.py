from uuid import UUID

from app.application.ai.retrieval.document_retrieval_service import (
    DocumentRetrievalService,
)
from app.application.knowledge.contracts.chunk_metadata import ChunkMetadata
from app.application.knowledge.contracts.retrieved_chunk import RetrievedChunk
from app.application.knowledge.contracts.vector_search_result import VectorSearchResult
from app.infrastructure.knowledge.rerank.simple_reranker import SimpleReranker


DOCUMENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
OWNER_ID = UUID("11111111-1111-1111-1111-111111111111")


def chunk(chunk_id: str) -> RetrievedChunk:
    return RetrievedChunk(
        content=chunk_id,
        metadata=ChunkMetadata(
            document_id=DOCUMENT_ID,
            filename="test.txt",
            chunk_id=chunk_id,
            chunk_index=0,
            page_number=None,
            owner_id=OWNER_ID,
        ),
        score=1.0,
    )


def test_rrf_combines_ranks_and_deduplicates_chunks():
    result = DocumentRetrievalService._fuse_with_rrf(
        semantic_result=VectorSearchResult(chunks=[chunk("a"), chunk("b")]),
        keyword_result=VectorSearchResult(chunks=[chunk("c"), chunk("a")]),
        top_k=3,
        rank_constant=60,
    )

    assert [item.metadata.chunk_id for item in result.chunks] == ["a", "c", "b"]
    assert len({item.metadata.chunk_id for item in result.chunks}) == 3
    assert result.chunks[0].score == (1 / 61) + (1 / 62)


def test_rrf_respects_top_k_and_empty_results():
    result = DocumentRetrievalService._fuse_with_rrf(
        semantic_result=VectorSearchResult(chunks=[chunk("a")]),
        keyword_result=VectorSearchResult(chunks=[chunk("b")]),
        top_k=1,
        rank_constant=60,
    )
    assert [item.metadata.chunk_id for item in result.chunks] == ["a"]

    empty = DocumentRetrievalService._fuse_with_rrf(
        semantic_result=VectorSearchResult(chunks=[]),
        keyword_result=VectorSearchResult(chunks=[]),
        top_k=20,
        rank_constant=60,
    )
    assert empty.chunks == []


def test_simple_reranker_prioritizes_query_overlap():
    chunks = [
        RetrievedChunk(
            content="This section is unrelated to the project timeline.",
            metadata=ChunkMetadata(
                document_id=DOCUMENT_ID,
                filename="test.txt",
                chunk_id="unrelated",
                chunk_index=0,
                page_number=None,
                owner_id=OWNER_ID,
            ),
            score=10.0,
        ),
        RetrievedChunk(
            content="Document ingestion and retrieval are handled by the enterprise RAG architecture.",
            metadata=ChunkMetadata(
                document_id=DOCUMENT_ID,
                filename="test.txt",
                chunk_id="relevant",
                chunk_index=1,
                page_number=None,
                owner_id=OWNER_ID,
            ),
            score=8.0,
        ),
        RetrievedChunk(
            content="The architecture handles document ingestion and retrieval with a hybrid pipeline.",
            metadata=ChunkMetadata(
                document_id=DOCUMENT_ID,
                filename="test.txt",
                chunk_id="best",
                chunk_index=2,
                page_number=None,
                owner_id=OWNER_ID,
            ),
            score=9.0,
        ),
    ]

    result = SimpleReranker().rerank(
        query="document ingestion retrieval architecture",
        chunks=chunks,
        top_k=2,
    )

    assert [item.metadata.chunk_id for item in result.chunks] == ["best", "relevant"]
