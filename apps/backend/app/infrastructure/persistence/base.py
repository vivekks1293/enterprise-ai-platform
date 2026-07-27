from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared SQLAlchemy metadata."""
    pass


# # Import all models so Alembic sees them
# from app.infrastructure.identity.models.user_model import UserModel
# from app.infrastructure.conversation.models.conversation_model import ConversationModel
# from app.infrastructure.conversation.models.message_model import MessageModel
# from app.infrastructure.knowledge.models.document_model import DocumentModel