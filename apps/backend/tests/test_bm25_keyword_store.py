import asyncio
from uuid import UUID

from app.application.knowledge.contracts.chunk_metadata import ChunkMetadata
from app.application.knowledge.contracts.document_chunk import DocumentChunk
from app.application.knowledge.contracts.vector_search_filter import VectorSearchFilter
from app.infrastructure.knowledge.keywordstore.bm25_keyword_store import BM25KeywordStore


OWNER_A = UUID("11111111-1111-1111-1111-111111111111")
OWNER_B = UUID("22222222-2222-2222-2222-222222222222")
DOCUMENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


def make_chunk(chunk_id: str, content: str, *, owner_id: UUID = OWNER_A) -> DocumentChunk:
    return DocumentChunk(
        content=content,
        metadata=ChunkMetadata(
            document_id=DOCUMENT_ID,
            filename="architecture.md",
            chunk_id=chunk_id,
            chunk_index=int(chunk_id[-1]),
            page_number=3,
            owner_id=owner_id,
        ),
    )


def test_bm25_indexes_ranks_and_preserves_metadata(tmp_path):
    asyncio.run(_test_bm25_indexes_ranks_and_preserves_metadata(tmp_path))


async def _test_bm25_indexes_ranks_and_preserves_metadata(tmp_path):
    store = BM25KeywordStore(tmp_path)
    target = make_chunk("chunk-3", "Content hash prevents redundant vector indexing.")
    await store.add([
        make_chunk("chunk-1", "Angular lazy loading improves application performance."),
        make_chunk("chunk-2", "Python FastAPI provides backend API services."),
        target,
    ])

    result = await store.search(
        query="redundant vector indexing",
        filter=VectorSearchFilter(owner_id=OWNER_A),
        top_k=2,
    )

    assert result.chunks[0].metadata == target.metadata
    assert result.chunks[0].content == target.content
    assert result.chunks[0].score > 0


def test_bm25_applies_owner_filter_top_k_and_empty_inputs(tmp_path):
    asyncio.run(_test_bm25_applies_owner_filter_top_k_and_empty_inputs(tmp_path))


async def _test_bm25_applies_owner_filter_top_k_and_empty_inputs(tmp_path):
    store = BM25KeywordStore(tmp_path)
    await store.add([
        make_chunk("chunk-1", "vector indexing vector indexing"),
        make_chunk("chunk-2", "vector indexing"),
        make_chunk("chunk-4", "vector indexing", owner_id=OWNER_B),
    ])

    result = await store.search(
        query="vector indexing",
        filter=VectorSearchFilter(owner_id=OWNER_A),
        top_k=1,
    )
    assert len(result.chunks) == 1
    assert result.chunks[0].metadata.owner_id == OWNER_A
    assert (await store.search(query="", filter=VectorSearchFilter(owner_id=OWNER_A), top_k=5)).chunks == []
    assert (await store.search(query="vector", filter=VectorSearchFilter(owner_id=OWNER_A), top_k=0)).chunks == []
    assert (await BM25KeywordStore(tmp_path / "empty").search(query="vector", filter=VectorSearchFilter(owner_id=OWNER_A), top_k=5)).chunks == []


def test_bm25_persists_and_upserts_duplicate_chunk_ids(tmp_path):
    asyncio.run(_test_bm25_persists_and_upserts_duplicate_chunk_ids(tmp_path))


async def _test_bm25_persists_and_upserts_duplicate_chunk_ids(tmp_path):
    store = BM25KeywordStore(tmp_path)
    await store.add([make_chunk("chunk-1", "obsolete deployment instructions")])
    await store.add([make_chunk("chunk-1", "content hash prevents redundant indexing")])

    reloaded = BM25KeywordStore(tmp_path)
    result = await reloaded.search(
        query="redundant indexing",
        filter=VectorSearchFilter(owner_id=OWNER_A),
        top_k=5,
    )

    assert [chunk.metadata.chunk_id for chunk in result.chunks] == ["chunk-1"]
    assert result.chunks[0].content == "content hash prevents redundant indexing"


def test_bm25_deletes_document_chunks_and_persists(tmp_path):
    asyncio.run(_test_bm25_deletes_document_chunks_and_persists(tmp_path))


async def _test_bm25_deletes_document_chunks_and_persists(tmp_path):
    store = BM25KeywordStore(tmp_path)
    other_doc_id = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    doc_a_chunk = make_chunk("chunk-1", "confidential project strategy details")
    doc_b_chunk = DocumentChunk(
        content="public guidelines and company policies",
        metadata=ChunkMetadata(
            document_id=other_doc_id,
            filename="guidelines.md",
            chunk_id="chunk-2",
            chunk_index=2,
            page_number=1,
            owner_id=OWNER_A,
        ),
    )
    doc_c_chunk = DocumentChunk(
        content="infrastructure deployment configuration guides",
        metadata=ChunkMetadata(
            document_id=other_doc_id,
            filename="infra.md",
            chunk_id="chunk-3",
            chunk_index=3,
            page_number=2,
            owner_id=OWNER_A,
        ),
    )
    await store.add([doc_a_chunk, doc_b_chunk, doc_c_chunk])

    # Verify both documents are present in search results
    res_before = await store.search(
        query="confidential strategy",
        filter=VectorSearchFilter(owner_id=OWNER_A),
        top_k=5,
    )
    assert DOCUMENT_ID in [c.metadata.document_id for c in res_before.chunks]
    assert res_before.chunks[0].metadata.document_id == DOCUMENT_ID

    # Delete DOCUMENT_ID
    await store.delete(DOCUMENT_ID)

    # Verify DOCUMENT_ID is gone from search and owner index
    res_after = await store.search(
        query="confidential strategy",
        filter=VectorSearchFilter(owner_id=OWNER_A),
        top_k=5,
    )
    assert DOCUMENT_ID not in [c.metadata.document_id for c in res_after.chunks]

    # Verify other document chunks remain intact
    res_b = await store.search(
        query="public guidelines",
        filter=VectorSearchFilter(owner_id=OWNER_A),
        top_k=5,
    )
    assert len(res_b.chunks) == 2
    assert all(c.metadata.document_id == other_doc_id for c in res_b.chunks)

    # Verify deletion persisted after re-instantiating store from disk
    reloaded = BM25KeywordStore(tmp_path)
    res_reloaded = await reloaded.search(
        query="confidential strategy",
        filter=VectorSearchFilter(owner_id=OWNER_A),
        top_k=5,
    )
    assert DOCUMENT_ID not in [c.metadata.document_id for c in res_reloaded.chunks]
    res_b_reloaded = await reloaded.search(
        query="public guidelines",
        filter=VectorSearchFilter(owner_id=OWNER_A),
        top_k=5,
    )
    assert all(c.metadata.document_id == other_doc_id for c in res_b_reloaded.chunks)


def test_bm25_filters_conversational_stopwords_from_query(tmp_path):
    asyncio.run(_test_bm25_filters_conversational_stopwords_from_query(tmp_path))


async def _test_bm25_filters_conversational_stopwords_from_query(tmp_path):
    store = BM25KeywordStore(tmp_path)
    vivek_chunk = make_chunk("chunk-1", "Vivek is an experienced Principal AI Architect and Lead Engineer.")
    other_chunk = make_chunk("chunk-2", "The system was configured and ok for production deployment.")
    third_chunk = make_chunk("chunk-3", "Database migrations and PostgreSQL query optimization.")
    await store.add([vivek_chunk, other_chunk, third_chunk])

    result = await store.search(
        query="ok and who was Vivek",
        filter=VectorSearchFilter(owner_id=OWNER_A),
        top_k=5,
    )

    assert len(result.chunks) >= 1
    assert result.chunks[0].metadata.chunk_id == "chunk-1"
    assert "Vivek" in result.chunks[0].content
    assert result.chunks[0].score > 0
    if len(result.chunks) > 1:
        assert result.chunks[0].score > result.chunks[1].score
