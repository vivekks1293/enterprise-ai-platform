from fastapi import FastAPI

from app.delivery.api.routers.health import router as health_router


def register_routers(app: FastAPI) -> None:
    app.include_router(
        health_router,
        prefix="/api/v1",
    )