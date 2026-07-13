from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.identity.entities.user import User
from app.domain.identity.repositories.user_repository import UserRepository
from app.domain.identity.value_objects.email import Email

from app.infrastructure.identity.mappers.user_mapper import to_domain
from app.infrastructure.identity.models.user_model import UserModel


class PostgresUserRepository(UserRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(
        self,
        email: Email,
    ) -> User | None:

        statement = select(UserModel).where(
            UserModel.email == str(email)
        )

        result = await self._session.execute(statement)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return to_domain(model)

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:

        statement = select(UserModel).where(
            UserModel.id == user_id
        )

        result = await self._session.execute(statement)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return to_domain(model)