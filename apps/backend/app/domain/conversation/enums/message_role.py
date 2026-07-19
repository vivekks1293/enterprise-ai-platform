from enum import Enum


class MessageRole(str, Enum):
    """
    Represents the author of a conversation message.

    Designed for future extensibility to support
    system prompts, tool calls, and agent workflows.
    """

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"