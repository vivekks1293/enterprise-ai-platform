from datetime import datetime, timezone
from uuid import UUID

from app.domain.identity.entities.user import RoleType, User
from app.domain.identity.repositories.user_repository import UserRepository
from app.domain.identity.value_objects.email import Email
from app.application.identity.ports.password_hasher import PasswordHasher


class InMemoryUserRepository(UserRepository):
    """
    In-memory implementation of the UserRepository.

    This repository exists to validate the Identity architecture
    before introducing PostgreSQL persistence.
    """

    def __init__(self, password_hasher: PasswordHasher,) -> None:
        demo_user = User(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            email=Email("admin@example.com"),
            hashed_password=password_hasher.hash(
                "Admin@123"
            ),
            # hashed_password="$2b$12$mfkOkIUN7BAI4FHE6/3Ct.XHNdQlkjMbXxmOYqj2EtzJWn9.RA.sG",
            name="Platform Administrator",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            role_type=RoleType.ADMIN,
            role_type_name="admin",
        )

        self._users: list[User] = [demo_user]

    async def create(self, user: User) -> None:
        self._users.append(user)

    async def get_by_email(
        self,
        email: Email,
    ) -> User | None:

        for user in self._users:
            if user.email == email:
                return user

        return None

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:

        for user in self._users:
            if user.id == user_id:
                return user

        return None