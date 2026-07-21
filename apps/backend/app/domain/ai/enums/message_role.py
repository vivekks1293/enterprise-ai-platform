from enum import Enum


class MessageRole(str, Enum):
    """Represents the role of a chat message."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"