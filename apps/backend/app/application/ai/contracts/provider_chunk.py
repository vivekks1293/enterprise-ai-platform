from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ProviderChunk:
    """
    Represents a streamed token or text fragment
    returned by an AI provider.
    """

    content: str