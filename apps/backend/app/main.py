from fastapi import FastAPI

from app.core.config.settings import settings
from app.core.logging.logger import configure_logging
from app.delivery.api.routers.health import router as health_router


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )

    app.include_router(health_router)

    return app


app = create_app()