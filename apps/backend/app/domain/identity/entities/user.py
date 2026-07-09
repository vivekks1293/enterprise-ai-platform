from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.identity.value_objects.email import Email


@dataclass(slots=True)
class User:
    """
    Domain entity representing an authenticated platform user.

    This entity is intentionally independent of any framework,
    database, or authentication technology.
    """

    id: UUID
    email: Email
    hashed_password: str
    name: str
    is_active: bool
    created_at: datetime