from dataclasses import dataclass

from app.domain.identity.value_objects.email import Email


@dataclass(frozen=True, slots=True)
class LoginRequest:
    """
    Input DTO for the Login use case.
    """

    email: Email
    password: str