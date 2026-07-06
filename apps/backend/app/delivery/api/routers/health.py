from fastapi import APIRouter

from app.delivery.api.schemas.health import HealthResponse

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "/live",
    response_model=HealthResponse,
)
def liveness() -> HealthResponse:
    return HealthResponse(
        status="UP",
    )


@router.get(
    "/ready",
    response_model=HealthResponse,
)
def readiness() -> HealthResponse:
    return HealthResponse(
        status="READY",
    )