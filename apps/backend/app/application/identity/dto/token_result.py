from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TokenResult:
    """
    Result returned by the TokenService after successfully
    generating an access token.
    """

    access_token: str
    expires_in: int
    token_type: str = "Bearer"