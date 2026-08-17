import asyncio
import json
from pathlib import Path
from uuid import UUID

from app.application.ai.retrieval.document_retrieval_service import (
    DocumentRetrievalService,
)
from app.core.config.settings import settings
from app.core.dependencies.knowledge import (
    get_embedding_provider,
    get_keyword_store,
    get_vector_store,
)
from app.evaluation.contracts.retrieval_evaluation_case import (
    RetrievalEvaluationCase,
)
from app.evaluation.run_retrieval_evaluation import (
    DATASET_PATH,
    EVALUATION_OWNER_ID,
    K,
    build_report_json,
    load_evaluation_cases,
)
from app.evaluation.runner.retrieval_evaluation_runner import (
    RetrievalEvaluationRunner,
)
from app.infrastructure.knowledge.rerank.cross_encoder_reranker import (
    CrossEncoderReranker,
)

REPORT_DIRECTORY = Path(__file__).parent / "reports"


async def evaluate_with_service(
    *,
    label: str,
    retrieval_service: DocumentRetrievalService,
    cases: list[RetrievalEvaluationCase],
    owner_id: UUID,
) -> dict:
    runner = RetrievalEvaluationRunner(retrieval_service=retrieval_service)
    report = await runner.run(
        cases=cases,
        owner_id=owner_id,
        k=K,
        retrieval_method="hybrid",
    )

    payload = {
        "label": label,
        "retrieval_method": report.retrieval_method,
        "summary": {
            "total_cases": report.total_cases,
            "k": report.k,
            "precision_at_k": report.precision_at_k,
            "recall_at_k": report.recall_at_k,
            "mean_reciprocal_rank": report.mean_reciprocal_rank,
        },
        "cases": build_report_json(report)["cases"],
    }

    REPORT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    output_path = REPORT_DIRECTORY / f"{label}_comparison.json"
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"{label} report saved to: {output_path}")
    return payload


async def main() -> None:
    cases = load_evaluation_cases()
    print(f"Loaded {len(cases)} evaluation cases from {DATASET_PATH}")

    embedding_provider = get_embedding_provider()
    vector_store = get_vector_store()
    keyword_store = get_keyword_store()

    baseline_service = DocumentRetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        keyword_store=keyword_store,
        reranker=None,
    )

    rerank_service = DocumentRetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        keyword_store=keyword_store,
        reranker=CrossEncoderReranker(),
    )

    baseline_report = await evaluate_with_service(
        label="hybrid",
        retrieval_service=baseline_service,
        cases=cases,
        owner_id=EVALUATION_OWNER_ID,
    )

    rerank_report = await evaluate_with_service(
        label="hybrid_rerank",
        retrieval_service=rerank_service,
        cases=cases,
        owner_id=EVALUATION_OWNER_ID,
    )

    summary = {
        "baseline": baseline_report["summary"],
        "hybrid_plus_rerank": rerank_report["summary"],
        "improvement": {
            "precision_at_k_delta": (
                rerank_report["summary"]["precision_at_k"]
                - baseline_report["summary"]["precision_at_k"]
            ),
            "recall_at_k_delta": (
                rerank_report["summary"]["recall_at_k"]
                - baseline_report["summary"]["recall_at_k"]
            ),
            "mean_reciprocal_rank_delta": (
                rerank_report["summary"]["mean_reciprocal_rank"]
                - baseline_report["summary"]["mean_reciprocal_rank"]
            ),
        },
        "rerank_model": settings.knowledge_rerank_model,
    }

    comparison_path = REPORT_DIRECTORY / "hybrid_vs_hybrid_rerank_summary.json"
    comparison_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print("Hybrid vs Hybrid + Rerank summary")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nSummary saved to: {comparison_path}")


if __name__ == "__main__":
    asyncio.run(main())
