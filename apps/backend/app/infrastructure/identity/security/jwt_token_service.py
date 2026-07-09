from datetime import timezone, datetime, timedelta
from uuid import UUID

import jwt

from app.application.identity.dto.token_result import TokenResult
from app.application.identity.exceptions import InvalidTokenError
from app.application.identity.ports.token_service import TokenService
from app.domain.identity.entities.user import User


class JwtTokenService(TokenService):
    """
    JWT implementation of the TokenService port.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        expiration_minutes: int,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expiration_minutes = expiration_minutes

    def generate_token(
        self,
        user: User,
    ) -> TokenResult:

        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(
            minutes=self._expiration_minutes
        )

        payload = {
            "sub": str(user.id),
            "iat": issued_at,
            "exp": expires_at,
        }

        access_token = jwt.encode(
            payload,
            self._secret_key,
            algorithm=self._algorithm,
        )

        return TokenResult(
            access_token=access_token,
            expires_in=self._expiration_minutes * 60,
        )

    def validate_token(
        self,
        token: str,
    ) -> UUID:

        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
            )

            return UUID(payload["sub"])

        except jwt.PyJWTError as exc:
            raise InvalidTokenError() from exc