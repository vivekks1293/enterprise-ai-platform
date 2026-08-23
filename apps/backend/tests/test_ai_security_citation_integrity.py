from uuid import UUID

from app.application.ai.services.citation_builder import CitationBuilder
from app.application.knowledge.contracts.chunk_metadata import ChunkMetadata
from app.application.knowledge.contracts.retrieved_chunk import RetrievedChunk


DOCUMENT_ID_A = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
DOCUMENT_ID_B = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
OWNER_ID = UUID("11111111-1111-1111-1111-111111111111")


def make_chunk(chunk_id: str, document_id: UUID, score: float) -> RetrievedChunk:
    return RetrievedChunk(
        content=f"content for {chunk_id}",
        metadata=ChunkMetadata(
            document_id=document_id,
            filename=f"{chunk_id}.txt",
            chunk_id=chunk_id,
            chunk_index=0,
            page_number=None,
            owner_id=OWNER_ID,
        ),
        score=score,
    )


def test_citations_are_derived_exclusively_from_retrieved_chunks():
    chunks = [
        make_chunk("chunk-1", DOCUMENT_ID_A, 0.9),
        make_chunk("chunk-2", DOCUMENT_ID_B, 0.7),
    ]

    citations = CitationBuilder.build(chunks)

    assert [c.document_id for c in citations] == [DOCUMENT_ID_A, DOCUMENT_ID_B]
    assert [c.chunk_id for c in citations] == ["chunk-1", "chunk-2"]
    assert [c.similarity_score for c in citations] == [0.9, 0.7]


def test_citation_ids_are_sequential_and_not_model_controlled():
    chunks = [make_chunk(f"chunk-{i}", DOCUMENT_ID_A, 0.5) for i in range(5)]

    citations = CitationBuilder.build(chunks)

    assert [c.citation_id for c in citations] == [1, 2, 3, 4, 5]


def test_no_citation_is_produced_without_a_corresponding_retrieved_chunk():
    citations = CitationBuilder.build([])

    assert citations == []


def test_citation_count_never_exceeds_retrieved_chunk_count():
    chunks = [make_chunk("chunk-1", DOCUMENT_ID_A, 0.5)]

    citations = CitationBuilder.build(chunks)

    assert len(citations) == len(chunks)
