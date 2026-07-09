from app.application.identity.dto.login_request import LoginRequest
from app.application.identity.dto.login_response import LoginResponse
from app.application.identity.dto.user_summary import user_summary
from app.application.identity.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
)
from app.application.identity.ports.password_hasher import PasswordHasher
from app.application.identity.ports.token_service import TokenService
from app.domain.identity.repositories.user_repository import UserRepository


class LoginUseCase:
    """
    Application use case responsible for authenticating a user.

    This use case orchestrates the authentication workflow without
    depending on any specific framework or infrastructure implementation.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_service = token_service

    async def execute(
        self,
        request: LoginRequest,
    ) -> LoginResponse:

        user = await self._user_repository.get_by_email(request.email)

        if user is None:
            raise InvalidCredentialsError()

        if not self._password_hasher.verify(
            request.password,
            user.hashed_password,
        ):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        token = self._token_service.generate_token(user)

        return LoginResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            expires_in=token.expires_in,
            user=user_summary(
                id=user.id,
                email=str(user.email),
                name=user.name,
            ),
        )