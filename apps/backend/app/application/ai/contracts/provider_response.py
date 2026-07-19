from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ProviderResponse:
    """
    Represents the completed response produced
    by an AI provider.
    """

    content: str

    input_tokens: int | None = None

    output_tokens: int | None = None

    finish_reason: str | None = None