import logging
from urllib.parse import urlparse

from sqlalchemy import text

from app.infrastructure.persistence.session import AsyncSessionFactory
from app.core.config.settings import settings

logger = logging.getLogger(__name__)


async def is_database_ready() -> bool:
    """
    Checks whether PostgreSQL is reachable.
    """

    try:
        parsed = urlparse(settings.database_url)

        logger.info(
            "Database connection target: "
            f"host={parsed.hostname} "
            f"port={parsed.port} "
            f"database={parsed.path.lstrip('/')}"
        )

        async with AsyncSessionFactory() as session:
            await session.execute(text("SELECT 1"))

        return True

    except Exception:
        logger.exception("Database readiness check failed")
        return False