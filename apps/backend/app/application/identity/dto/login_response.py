from dataclasses import dataclass

from app.application.identity.dto.user_summary import user_summary


@dataclass(frozen=True, slots=True)
class LoginResponse:
    """
    Output DTO for a successful login.
    """

    access_token: str
    token_type: str
    expires_in: int
    user: user_summary