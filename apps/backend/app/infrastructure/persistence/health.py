from sqlalchemy import text

from app.infrastructure.persistence.session import AsyncSessionFactory


async def is_database_ready() -> bool:
    """
    Checks whether PostgreSQL is reachable.

    Executes a lightweight query against the database.

    Returns:
        True if the database is reachable.
        False otherwise.
    """

    try:
        async with AsyncSessionFactory() as session:
            await session.execute(text("SELECT 1"))

        return True

    except Exception:
        return False