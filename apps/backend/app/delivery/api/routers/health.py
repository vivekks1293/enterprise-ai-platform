from fastapi import APIRouter, HTTPException

from app.delivery.api.schemas.health import HealthResponse
from app.infrastructure.persistence.health import is_database_ready

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "/live",
    response_model=HealthResponse,
)
async def liveness() -> HealthResponse:
    """
    Liveness probe.

    Indicates that the application process is running.
    Does not depend on external services.
    """

    return HealthResponse(
        status="UP",
    )


@router.get(
    "/ready",
    response_model=HealthResponse,
)
async def readiness() -> HealthResponse:
    """
    Readiness probe.

    Indicates that the application is ready
    to serve requests.
    """

    database_ready = await is_database_ready()

    if not database_ready:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )

    return HealthResponse(
        status="READY",
    )