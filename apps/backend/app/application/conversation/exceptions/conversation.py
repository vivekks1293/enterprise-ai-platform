"""
Conversation-related application exceptions.
"""


class ConversationError(Exception):
    """
    Base exception for all conversation-related application errors.
    """

    def __init__(self, message: str = "Conversation error.") -> None:
        super().__init__(message)


class ConversationNotFoundError(ConversationError):
    """
    Raised when the requested conversation
    does not exist or does not belong to
    the authenticated user.
    """

    def __init__(self) -> None:
        super().__init__("Conversation not found.")


class ConversationAccessDeniedError(ConversationError):
    """
    Raised when a user attempts to access
    a conversation without permission.
    """

    def __init__(self) -> None:
        super().__init__("Access denied to conversation.")