from datetime import datetime, timezone
from uuid import uuid4

from app.application.common.ports.unit_of_work import UnitOfWork
from app.application.identity.dto.create_user import (
    CreateUserRequest,
    CreateUserResponse,
)
from app.application.identity.exceptions import UserAlreadyExistsError
from app.application.identity.ports.password_hasher import PasswordHasher
from app.domain.identity.entities.user import User
from app.domain.identity.repositories.user_repository import UserRepository


class CreateUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._unit_of_work = unit_of_work

    async def execute(
        self,
        request: CreateUserRequest,
    ) -> CreateUserResponse:
        if await self._user_repository.get_by_email(request.email):
            raise UserAlreadyExistsError()

        user = User(
            id=uuid4(),
            email=request.email,
            hashed_password=self._password_hasher.hash(request.password),
            name=str(request.email),
            is_active=True,
            created_at=datetime.now(timezone.utc),
            role_type=request.role_type,
            role_type_name=request.role_type_name,
        )

        try:
            await self._user_repository.create(user)
            await self._unit_of_work.commit()
        except Exception:
            await self._unit_of_work.rollback()
            raise

        return CreateUserResponse(
            id=user.id,
            email=str(user.email),
            name=user.name,
            role_type=user.role_type,
            role_type_name=user.role_type_name,
        )