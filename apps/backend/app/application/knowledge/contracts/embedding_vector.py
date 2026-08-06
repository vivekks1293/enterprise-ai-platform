from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingVector:
    """
    Numerical representation of text.
    """

    values: list[float]