from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select

from app.domain.identity.value_objects.email import Email
from app.infrastructure.identity.mappers.user_mapper import to_model
from app.domain.identity.entities.user import User
from app.infrastructure.identity.models.user_model import UserModel
from app.infrastructure.identity.security.bcrypt_password_hasher import (
    BCryptPasswordHasher,
)
from app.infrastructure.persistence.session import AsyncSessionFactory


ADMIN_EMAIL = "vivek1293@gmail.com"
ADMIN_PASSWORD = "Vivek@123"


async def seed_admin() -> None:
    """
    Creates the default administrator account if it does not exist.
    """

    async with AsyncSessionFactory() as session:

        existing = await session.execute(
            select(UserModel).where(
                UserModel.email == ADMIN_EMAIL
            )
        )

        if existing.scalar_one_or_none():
            print("Admin user already exists.")
            return

        hasher = BCryptPasswordHasher()

        admin = User(
            id=uuid4(),
            email=Email(ADMIN_EMAIL),
            hashed_password=hasher.hash(ADMIN_PASSWORD),
            name="Platform Administrator",
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )

        session.add(to_model(admin))

        await session.commit()

        print("Admin user created successfully.")