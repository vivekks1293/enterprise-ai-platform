from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationEvaluationCase:
    """Expected evidence and facts for one generation evaluation question."""

    id: str

    question: str

    relevant_chunk_ids: set[str]

    expected_facts: list[str]