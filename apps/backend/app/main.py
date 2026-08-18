from fastapi import FastAPI

from app.core.config.settings import settings
from app.core.lifespan import lifespan
from app.core.logging.logger import configure_logging
from app.delivery.api import register_routers
from app.core.exceptions import register_exception_handlers
from app.core.middleware import RequestCorrelationMiddleware, register_cors



def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Enterprise AI Platform Backend API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(RequestCorrelationMiddleware)
    register_cors(app)
    register_exception_handlers(app)
    register_routers(app)


    return app


app = create_app()