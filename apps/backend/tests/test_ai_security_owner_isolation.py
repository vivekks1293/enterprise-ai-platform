import asyncio
from uuid import UUID

from app.application.ai.retrieval.document_retrieval_service import (
    DocumentRetrievalService,
)
from app.application.knowledge.contracts.chunk_metadata import ChunkMetadata
from app.application.knowledge.contracts.embedding_vector import EmbeddingVector
from app.application.knowledge.contracts.retrieved_chunk import RetrievedChunk
from app.application.knowledge.contracts.vector_search_filter import (
    VectorSearchFilter,
)
from app.application.knowledge.contracts.vector_search_result import (
    VectorSearchResult,
)
from app.infrastructure.knowledge.keywordstore.bm25_keyword_store import (
    BM25KeywordStore,
)
from app.application.knowledge.contracts.document_chunk import DocumentChunk


OWNER_A = UUID("11111111-1111-1111-1111-111111111111")
OWNER_B = UUID("22222222-2222-2222-2222-222222222222")
DOCUMENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


def chunk(chunk_id: str, owner_id: UUID) -> RetrievedChunk:
    return RetrievedChunk(
        content=f"content for {chunk_id}",
        metadata=ChunkMetadata(
            document_id=DOCUMENT_ID,
            filename="doc.txt",
            chunk_id=chunk_id,
            chunk_index=0,
            page_number=None,
            owner_id=owner_id,
        ),
        score=1.0,
    )


class OwnerAwareVectorStore:
    """Fake vector store that only returns chunks matching the requested owner."""

    def __init__(self, chunks_by_owner: dict[UUID, list[RetrievedChunk]]) -> None:
        self._chunks_by_owner = chunks_by_owner
        self.received_filters: list[VectorSearchFilter] = []

    async def search(
        self, *, embedding: EmbeddingVector, filter: VectorSearchFilter, top_k: int
    ) -> VectorSearchResult:
        self.received_filters.append(filter)
        return VectorSearchResult(
            chunks=self._chunks_by_owner.get(filter.owner_id, [])[:top_k]
        )


class OwnerAwareKeywordStore:
    """Fake keyword store that only returns chunks matching the requested owner."""

    def __init__(self, chunks_by_owner: dict[UUID, list[RetrievedChunk]]) -> None:
        self._chunks_by_owner = chunks_by_owner
        self.received_filters: list[VectorSearchFilter] = []

    async def search(
        self, *, query: str, filter: VectorSearchFilter, top_k: int
    ) -> VectorSearchResult:
        self.received_filters.append(filter)
        return VectorSearchResult(
            chunks=self._chunks_by_owner.get(filter.owner_id, [])[:top_k]
        )


class StubEmbeddingProvider:
    async def embed_query(self, query: str) -> EmbeddingVector:
        return EmbeddingVector(values=[0.1, 0.2])


class IdentityReranker:
    """Reranker stub that only reorders/limits the chunks it was given."""

    def rerank(self, *, query: str, chunks, top_k: int) -> VectorSearchResult:
        return VectorSearchResult(chunks=list(reversed(chunks))[:top_k])


def make_service(reranker=None) -> DocumentRetrievalService:
    chunks_by_owner = {
        OWNER_A: [chunk("owner-a-chunk", OWNER_A)],
        OWNER_B: [chunk("owner-b-chunk", OWNER_B)],
    }
    return DocumentRetrievalService(
        embedding_provider=StubEmbeddingProvider(),
        vector_store=OwnerAwareVectorStore(chunks_by_owner),
        keyword_store=OwnerAwareKeywordStore(chunks_by_owner),
        reranker=reranker,
    )


def test_semantic_retrieval_is_isolated_per_owner():
    service = make_service()

    result_a = asyncio.run(
        service.retrieve(query="q", owner_id=OWNER_A, retrieval_mode="semantic")
    )
    result_b = asyncio.run(
        service.retrieve(query="q", owner_id=OWNER_B, retrieval_mode="semantic")
    )

    assert [c.metadata.chunk_id for c in result_a.chunks] == ["owner-a-chunk"]
    assert [c.metadata.chunk_id for c in result_b.chunks] == ["owner-b-chunk"]


def test_keyword_retrieval_is_isolated_per_owner():
    service = make_service()

    result_a = asyncio.run(
        service.retrieve(query="q", owner_id=OWNER_A, retrieval_mode="keyword")
    )
    result_b = asyncio.run(
        service.retrieve(query="q", owner_id=OWNER_B, retrieval_mode="keyword")
    )

    assert [c.metadata.chunk_id for c in result_a.chunks] == ["owner-a-chunk"]
    assert [c.metadata.chunk_id for c in result_b.chunks] == ["owner-b-chunk"]


def test_hybrid_rrf_retrieval_is_isolated_per_owner():
    service = make_service()

    result_a = asyncio.run(
        service.retrieve(query="q", owner_id=OWNER_A, retrieval_mode="hybrid")
    )
    result_b = asyncio.run(
        service.retrieve(query="q", owner_id=OWNER_B, retrieval_mode="hybrid")
    )

    assert all(c.metadata.owner_id == OWNER_A for c in result_a.chunks)
    assert all(c.metadata.owner_id == OWNER_B for c in result_b.chunks)


def test_reranking_cannot_introduce_chunks_from_another_owner():
    service = make_service(reranker=IdentityReranker())

    result_a = asyncio.run(
        service.retrieve(query="q", owner_id=OWNER_A, retrieval_mode="semantic")
    )

    assert all(c.metadata.owner_id == OWNER_A for c in result_a.chunks)


def test_bm25_store_user_a_cannot_retrieve_user_b_documents(tmp_path):
    asyncio.run(_bm25_isolation(tmp_path))


async def _bm25_isolation(tmp_path):
    store = BM25KeywordStore(tmp_path)
    await store.add(
        [
            DocumentChunk(
                content="owner a confidential contract terms",
                metadata=ChunkMetadata(
                    document_id=DOCUMENT_ID,
                    filename="a.txt",
                    chunk_id="a-chunk",
                    chunk_index=0,
                    page_number=None,
                    owner_id=OWNER_A,
                ),
            ),
            DocumentChunk(
                content="owner b confidential contract terms",
                metadata=ChunkMetadata(
                    document_id=DOCUMENT_ID,
                    filename="b.txt",
                    chunk_id="b-chunk",
                    chunk_index=0,
                    page_number=None,
                    owner_id=OWNER_B,
                ),
            ),
        ]
    )

    result_for_a = await store.search(
        query="confidential contract terms",
        filter=VectorSearchFilter(owner_id=OWNER_A),
        top_k=10,
    )
    result_for_b = await store.search(
        query="confidential contract terms",
        filter=VectorSearchFilter(owner_id=OWNER_B),
        top_k=10,
    )

    assert [c.metadata.chunk_id for c in result_for_a.chunks] == ["a-chunk"]
    assert [c.metadata.chunk_id for c in result_for_b.chunks] == ["b-chunk"]
