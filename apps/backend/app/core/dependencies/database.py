from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.session import AsyncSessionFactory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a request-scoped database session.
    """

    async with AsyncSessionFactory() as session:
        yield session