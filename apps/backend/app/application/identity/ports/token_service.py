from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.identity.entities.user import User


class TokenService(ABC):
    """
    Application port for issuing and validating identity tokens.
    """

    @abstractmethod
    def generate_token(self, user: User) -> str:
        """
        Generate an access token representing the authenticated user.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_token(self, token: str) -> UUID:
        """
        Validate an access token and return the authenticated user's ID.

        Raises an application exception if the token is invalid.
        """
        raise NotImplementedError