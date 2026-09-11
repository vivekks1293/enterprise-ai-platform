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


async def get_database_diagnostic() -> dict:
    """
    Temporary diagnostic query to confirm which PostgreSQL database the
    running application is connected to without exposing credentials.
    """
    try:
        async with AsyncSessionFactory() as session:
            current_database = (await session.execute(text("SELECT current_database()"))).scalar()
            current_schema = (await session.execute(text("SELECT current_schema()"))).scalar()
            current_user = (await session.execute(text("SELECT current_user"))).scalar()
            inet_server_addr = (await session.execute(text("SELECT inet_server_addr()"))).scalar()
            inet_server_port = (await session.execute(text("SELECT inet_server_port()"))).scalar()
            search_path = (await session.execute(text("SELECT current_setting('search_path')"))).scalar()
            table_result = (await session.execute(text("SELECT to_regclass('public.users')"))).scalar()

            diagnostic = {
                "current_database": current_database,
                "current_schema": current_schema,
                "current_user": current_user,
                "inet_server_addr": str(inet_server_addr) if inet_server_addr is not None else None,
                "inet_server_port": inet_server_port,
                "search_path": search_path,
                "table_exists": table_result is not None,
            }

            logger.info(
                "Database diagnostic",
                extra={
                    "current_database": diagnostic["current_database"],
                    "current_schema": diagnostic["current_schema"],
                    "current_user": diagnostic["current_user"],
                    "inet_server_addr": diagnostic["inet_server_addr"],
                    "inet_server_port": diagnostic["inet_server_port"],
                    "search_path": diagnostic["search_path"],
                    "table_exists": diagnostic["table_exists"],
                },
            )

            return diagnostic
    except Exception:
        logger.exception("Database diagnostic failed")
        return {
            "current_database": None,
            "current_schema": None,
            "current_user": None,
            "inet_server_addr": None,
            "inet_server_port": None,
            "search_path": None,
            "table_exists": False,
        }