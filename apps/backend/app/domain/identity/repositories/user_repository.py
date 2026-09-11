from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.identity.entities.user import User
from app.domain.identity.value_objects.email import Email


class UserRepository(ABC):
    """
    Domain repository contract for retrieving platform users.
    """

    @abstractmethod
    async def create(self, user: User) -> None:
        """Persist a new user."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        """
        Retrieve a user by email.

        Returns None if no matching user exists.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Retrieve a user by unique identifier.

        Returns None if no matching user exists.
        """
        raise NotImplementedError