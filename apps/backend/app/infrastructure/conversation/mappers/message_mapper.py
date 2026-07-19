from app.domain.conversation.entities.message import Message
from app.domain.conversation.enums.message_role import MessageRole
from app.infrastructure.conversation.models.message_model import (
    MessageModel,
)


def to_domain(model: MessageModel) -> Message:
    """
    Maps a SQLAlchemy MessageModel to a Domain Message.
    """

    return Message(
        id=model.id,
        conversation_id=model.conversation_id,
        role=MessageRole(model.role),
        content=model.content,
        created_at=model.created_at,
    )


def to_model(entity: Message) -> MessageModel:
    """
    Maps a Domain Message to a SQLAlchemy MessageModel.
    """

    return MessageModel(
        id=entity.id,
        conversation_id=entity.conversation_id,
        role=entity.role.value,
        content=entity.content,
        created_at=entity.created_at,
    )