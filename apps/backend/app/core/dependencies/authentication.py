from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.identity.exceptions import (
    UserNotFoundError,
)
from app.core.dependencies.identity import (
    get_token_service,
    get_user_repository,
)
from app.domain.identity.entities.user import User
from app.domain.identity.repositories.user_repository import UserRepository

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    """
    Resolve the authenticated user from the Authorization header.
    """

    token_service = get_token_service()

    user_id = token_service.validate_token(
        credentials.credentials,
    )

    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise UserNotFoundError()

    return user