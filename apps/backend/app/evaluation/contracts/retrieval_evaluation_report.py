from dataclasses import dataclass

from app.evaluation.contracts.retrieval_evaluation_result import (
    RetrievalEvaluationResult,
)


@dataclass(frozen=True)
class RetrievalEvaluationReport:
    """
    Aggregated retrieval evaluation report.
    """

    total_cases: int

    k: int

    precision_at_k: float

    recall_at_k: float

    mean_reciprocal_rank: float

    results: list[RetrievalEvaluationResult]