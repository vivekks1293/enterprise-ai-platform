from functools import lru_cache

from fastapi import Depends
# from sqlalchemy.orm import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.identity.ports.password_hasher import PasswordHasher
from app.application.identity.ports.token_service import TokenService
from app.application.identity.use_cases.get_current_user import (
    GetCurrentUserUseCase,
)
from app.application.identity.use_cases.login import LoginUseCase
from app.application.identity.use_cases.logout import LogoutUseCase

from app.core.config.settings import settings
from app.core.dependencies.database import get_db_session

from app.domain.identity.repositories.user_repository import UserRepository

from app.infrastructure.identity.repositories.postgres_user_repository import (
    PostgresUserRepository,
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
    Singleton BCrypt password hasher.
    """
    return BCryptPasswordHasher()


@lru_cache
def get_token_service() -> TokenService:
    """
    Singleton JWT token service.
    """
    return JwtTokenService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expiration_minutes=settings.jwt_expiration_minutes,
    )


def get_user_repository(
    session: AsyncSession  = Depends(get_db_session),
) -> UserRepository:
    """
    Returns the PostgreSQL implementation of UserRepository.

    Repository lifetime is request scoped because it owns
    a request scoped SQLAlchemy session.
    """
    return PostgresUserRepository(session=session)


# ==========================================================
# Application Providers
# ==========================================================


def get_login_use_case(
    repository: UserRepository = Depends(get_user_repository),
) -> LoginUseCase:
    """
    Constructs LoginUseCase.
    """

    return LoginUseCase(
        user_repository=repository,
        password_hasher=get_password_hasher(),
        token_service=get_token_service(),
    )


def get_current_user_use_case() -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase()


def get_logout_use_case() -> LogoutUseCase:
    return LogoutUseCase()