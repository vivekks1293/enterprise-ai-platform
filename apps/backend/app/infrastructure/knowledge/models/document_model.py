from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, Index, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.base import Base


class DocumentModel(Base):
    """
    SQLAlchemy persistence model for a knowledge document.
    """

    __tablename__ = "documents"

    __table_args__ = (
        Index("ix_documents_owner_id", "owner_id"),
        Index("ix_documents_status", "status"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
    )

    owner_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    storage_key: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        unique=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )