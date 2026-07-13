# app/infrastructure/persistence/base.py

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    Every persistence model in the application should inherit
    from this class so that SQLAlchemy and Alembic share a
    single metadata registry.
    """

    pass