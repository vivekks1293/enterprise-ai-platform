from app.domain.conversation.entities.conversation import Conversation
from app.infrastructure.conversation.models.conversation_model import (
    ConversationModel,
)


def to_domain(model: ConversationModel) -> Conversation:
    """
    Maps a SQLAlchemy ConversationModel to a Domain Conversation.
    """

    return Conversation(
        id=model.id,
        owner_id=model.owner_id,
        title=model.title,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def to_model(entity: Conversation) -> ConversationModel:
    """
    Maps a Domain Conversation to a SQLAlchemy ConversationModel.
    """

    return ConversationModel(
        id=entity.id,
        owner_id=entity.owner_id,
        title=entity.title,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )