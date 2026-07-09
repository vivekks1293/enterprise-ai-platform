from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """
    Application port for password hashing operations.
    """

    @abstractmethod
    def hash(self, password: str) -> str:
        """Return a secure hash for the given password."""
        raise NotImplementedError

    @abstractmethod
    def verify(self, password: str, hashed_password: str) -> bool:
        """Verify a plain-text password against a stored hash."""
        raise NotImplementedError