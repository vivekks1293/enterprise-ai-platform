from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.base import Base
from app.infrastructure.conversation.models.message_citation_model import (
    MessageCitationModel,
)

class MessageModel(Base):
    """
    SQLAlchemy model representing a persisted conversation message.
    """

    __tablename__ = "messages"

    __table_args__ = (
        Index("ix_messages_conversation_id", "conversation_id"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
    )

    conversation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    conversation: Mapped["ConversationModel"] = relationship(
        "ConversationModel",
        back_populates="messages",
    )

    citations: Mapped[list["MessageCitationModel"]] = relationship(
        "MessageCitationModel",
        back_populates="message",
        cascade="all, delete-orphan",
    )