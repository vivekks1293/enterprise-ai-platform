from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ChatUsage:
    """Token usage information."""

    prompt_tokens: int | None = None

    completion_tokens: int | None = None

    total_tokens: int | None = None