from uuid import UUID

from app.application.ai.retrieval.document_retrieval_service import (
    DocumentRetrievalService,
)
from app.evaluation.contracts.retrieval_evaluation_case import (
    RetrievalEvaluationCase,
)
from app.evaluation.contracts.retrieval_evaluation_report import (
    RetrievalEvaluationReport,
)
from app.evaluation.contracts.retrieval_evaluation_result import (
    RetrievalEvaluationResult, RetrievedEvaluationChunk
)
from app.evaluation.metrics.retrieval_metrics import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


class RetrievalEvaluationRunner:
    """
    Executes retrieval evaluation cases against the
    production retrieval pipeline.
    """

    def __init__(
        self,
        retrieval_service: DocumentRetrievalService,
    ) -> None:
        self._retrieval_service = retrieval_service

    async def run(
        self,
        *,
        cases: list[RetrievalEvaluationCase],
        owner_id: UUID,
        k: int,
    ) -> RetrievalEvaluationReport:
        """
        Executes all evaluation cases and produces
        an aggregated retrieval evaluation report.
        """

        if k <= 0:
            raise ValueError(
                "k must be greater than zero."
            )

        if not cases:
            return RetrievalEvaluationReport(
                total_cases=0,
                k=k,
                precision_at_k=0.0,
                recall_at_k=0.0,
                mean_reciprocal_rank=0.0,
                results=[],
            )

        results: list[RetrievalEvaluationResult] = []

        for case in cases:

            retrieval = await self._retrieval_service.retrieve(
                query=case.question,
                owner_id=owner_id,
                top_k=k,
            )

            retrieved_chunk_ids = [
                chunk.metadata.chunk_id
                for chunk in retrieval.chunks
            ]

            retrieved_chunks = [
                RetrievedEvaluationChunk(
                    rank=rank,
                    chunk_id=chunk.metadata.chunk_id,
                    distance=chunk.distance,
                    filename=chunk.metadata.filename,
                    page_number=chunk.metadata.page_number,
                    content=chunk.content,
                )
                for rank, chunk in enumerate(
                    retrieval.chunks,
                    start=1,
                )
            ]

            precision = precision_at_k(
                retrieved_chunk_ids=retrieved_chunk_ids,
                relevant_chunk_ids=case.relevant_chunk_ids,
                k=k,
            )

            recall = recall_at_k(
                retrieved_chunk_ids=retrieved_chunk_ids,
                relevant_chunk_ids=case.relevant_chunk_ids,
                k=k,
            )

            rank = reciprocal_rank(
                retrieved_chunk_ids=retrieved_chunk_ids,
                relevant_chunk_ids=case.relevant_chunk_ids,
            )

            results.append(
                RetrievalEvaluationResult(
                    case_id=case.id,
                    question=case.question,
                    retrieved_chunks=retrieved_chunks,
                    relevant_chunk_ids=case.relevant_chunk_ids,
                    precision_at_k=precision,
                    recall_at_k=recall,
                    reciprocal_rank=rank,
                )
            )

        total_cases = len(results)

        return RetrievalEvaluationReport(
            total_cases=total_cases,
            k=k,
            precision_at_k=(
                sum(
                    result.precision_at_k
                    for result in results
                )
                / total_cases
            ),
            recall_at_k=(
                sum(
                    result.recall_at_k
                    for result in results
                )
                / total_cases
            ),
            mean_reciprocal_rank=(
                sum(
                    result.reciprocal_rank
                    for result in results
                )
                / total_cases
            ),
            results=results,
        )