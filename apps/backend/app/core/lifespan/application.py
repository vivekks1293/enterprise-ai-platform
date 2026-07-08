from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting...")

    # Future:
    # Initialize PostgreSQL
    # Initialize ChromaDB
    # Initialize DI Container
    # Initialize Telemetry

    yield

    logger.info("Application shutting down...")

    # Future:
    # Close PostgreSQL
    # Close ChromaDB
    # Dispose Resources