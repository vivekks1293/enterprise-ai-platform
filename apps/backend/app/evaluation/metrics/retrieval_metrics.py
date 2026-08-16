def precision_at_k(
    *,
    retrieved_chunk_ids: list[str],
    relevant_chunk_ids: set[str],
    k: int,
) -> float:
    """
    Calculates Precision@K.

    Precision@K =
        relevant retrieved results in top K
        /
        K
    """

    if k <= 0:
        raise ValueError("k must be greater than zero.")

    retrieved = retrieved_chunk_ids[:k]

    if not retrieved:
        return 0.0

    relevant_retrieved = sum(
        1
        for chunk_id in retrieved
        if chunk_id in relevant_chunk_ids
    )

    return relevant_retrieved / len(retrieved)


def recall_at_k(
    *,
    retrieved_chunk_ids: list[str],
    relevant_chunk_ids: set[str],
    k: int,
) -> float:
    """
    Calculates Recall@K.

    Recall@K =
        relevant retrieved results in top K
        /
        total relevant results
    """

    if k <= 0:
        raise ValueError("k must be greater than zero.")

    if not relevant_chunk_ids:
        return 0.0

    retrieved = set(
        retrieved_chunk_ids[:k]
    )

    relevant_retrieved = retrieved.intersection(
        relevant_chunk_ids
    )

    return len(relevant_retrieved) / len(
        relevant_chunk_ids
    )


def reciprocal_rank(
    *,
    retrieved_chunk_ids: list[str],
    relevant_chunk_ids: set[str],
) -> float:
    """
    Calculates Reciprocal Rank.

    Returns:
        1 / rank of the first relevant result.

    Returns 0.0 when no relevant result is retrieved.
    """

    if not relevant_chunk_ids:
        return 0.0

    for index, chunk_id in enumerate(
        retrieved_chunk_ids,
        start=1,
    ):
        if chunk_id in relevant_chunk_ids:
            return 1.0 / index

    return 0.0