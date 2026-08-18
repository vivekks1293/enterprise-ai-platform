from uuid import UUID

from app.application.knowledge.contracts.chunk_metadata import ChunkMetadata
from app.application.knowledge.contracts.retrieved_chunk import RetrievedChunk
from app.domain.ai.models.citation import Citation
from app.evaluation.contracts.generation_evaluation_case import (
    GenerationEvaluationCase,
)
from app.evaluation.contracts.generation_evaluation_record import (
    GenerationEvaluationRecord,
)


DOCUMENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
OWNER_ID = UUID("11111111-1111-1111-1111-111111111111")


def test_generation_evaluation_contracts_preserve_evidence_and_facts():
    chunk = RetrievedChunk(
        content="Approvals take five business days.",
        metadata=ChunkMetadata(
            document_id=DOCUMENT_ID,
            filename="approval-policy.pdf",
            chunk_id="approval-period",
            chunk_index=0,
            page_number=12,
            owner_id=OWNER_ID,
        ),
        score=0.91,
    )
    citation = Citation(
        citation_id=1,
        document_id=DOCUMENT_ID,
        chunk_id="approval-period",
        filename="approval-policy.pdf",
        page_number=12,
        similarity_score=0.91,
    )

    record = GenerationEvaluationRecord(
        question="How long do approvals take?",
        answer="Approvals take five business days.",
        selected_chunks=[chunk],
        citations=[citation],
    )
    case = GenerationEvaluationCase(
        id="approval-period",
        question=record.question,
        relevant_chunk_ids={"approval-period"},
        expected_facts=["Approvals take five business days."],
    )

    assert record.selected_chunks == [chunk]
    assert record.citations == [citation]
    assert case.relevant_chunk_ids == {"approval-period"}
    assert case.expected_facts == ["Approvals take five business days."]