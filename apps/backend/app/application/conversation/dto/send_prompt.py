from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class SendPromptRequest:
    """
    Request for sending a prompt
    within a conversation.
    """

    conversation_id: UUID

    owner_id: UUID

    prompt: str