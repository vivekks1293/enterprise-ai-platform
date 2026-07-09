from functools import lru_cache

from app.application.identity.ports.password_hasher import PasswordHasher
from app.application.identity.ports.token_service import TokenService
from app.application.identity.use_cases.get_current_user import (
    GetCurrentUserUseCase,
)
from app.application.identity.use_cases.login import LoginUseCase
from app.application.identity.use_cases.logout import LogoutUseCase
from app.core.config.settings import settings
from app.domain.identity.repositories.user_repository import UserRepository
from app.infrastructure.identity.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)
from app.infrastructure.identity.security.bcrypt_password_hasher import (
    BCryptPasswordHasher,
)
from app.infrastructure.identity.security.jwt_token_service import (
    JwtTokenService,
)


# ==========================================================
# Infrastructure Providers
# ==========================================================


@lru_cache
def get_password_hasher() -> PasswordHasher:
    """
    Returns the application's password hashing implementation.
    """
    return BCryptPasswordHasher()


@lru_cache
def get_token_service() -> TokenService:
    """
    Returns the application's token service implementation.
    """
    return JwtTokenService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expiration_minutes=settings.jwt_expiration_minutes,
    )


@lru_cache
def get_user_repository() -> UserRepository:
    """
    Returns the application's user repository.

    Sprint 1B uses an in-memory implementation.
    This can later be replaced with PostgreSQL
    without changing any application code.
    """
    return InMemoryUserRepository(password_hasher=get_password_hasher())


# ==========================================================
# Application Providers
# ==========================================================


def get_login_use_case() -> LoginUseCase:
    """
    Constructs the Login use case.
    """
    return LoginUseCase(
        user_repository=get_user_repository(),
        password_hasher=get_password_hasher(),
        token_service=get_token_service(),
    )


def get_current_user_use_case() -> GetCurrentUserUseCase:
    """
    Constructs the GetCurrentUser use case.
    """
    return GetCurrentUserUseCase()


def get_logout_use_case() -> LogoutUseCase:
    """
    Constructs the Logout use case.
    """
    return LogoutUseCase()