from fastapi import FastAPI

from app.delivery.api.routers.health import router as health_router
from app.delivery.api.routers.identity import router as identity_router


def register_routers(app: FastAPI) -> None:
    app.include_router(
        health_router,
        prefix="/api/v1",
    )

    app.include_router(
        identity_router,
        prefix="/api/v1",
    )