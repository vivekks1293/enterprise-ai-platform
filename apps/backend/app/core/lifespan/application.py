from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging.logger import logger
from app.infrastructure.persistence.health import is_database_ready
from app.core.observability.langfuse import get_langfuse_observer


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Application starting...")

    database_ready = await is_database_ready()

    if database_ready:
        logger.info("PostgreSQL connection established.")
    else:
        logger.error("Unable to connect to PostgreSQL.")

    yield

    await get_langfuse_observer().shutdown()

    logger.info("Application shutting down...")