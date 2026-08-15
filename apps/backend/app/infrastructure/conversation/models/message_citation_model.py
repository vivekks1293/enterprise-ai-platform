from uuid import UUID

from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.base import Base


class MessageCitationModel(Base):
    """
    Stores evidence supporting an assistant message.
    """

    __tablename__ = "message_citations"

    message_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        primary_key=True,
    )

    document_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
    )

    chunk_id: Mapped[str] = mapped_column(
        nullable=False,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    similarity_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    message = relationship(
        "MessageModel",
        back_populates="citations",
    )