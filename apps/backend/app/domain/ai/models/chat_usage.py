from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ChatUsage:
    """Token usage information."""

    prompt_tokens: int = 0

    completion_tokens: int = 0

    total_tokens: int = 0