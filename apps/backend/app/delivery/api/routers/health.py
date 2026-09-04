from fastapi import APIRouter, HTTPException

from app.delivery.api.schemas.health import DatabaseDiagnosticResponse, HealthResponse
from app.infrastructure.persistence.health import get_database_diagnostic, is_database_ready

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


@router.get(
    "/diagnostic-db-connection",
    response_model=DatabaseDiagnosticResponse,
)
async def diagnostic_db_connection() -> DatabaseDiagnosticResponse:
    """
    Temporary diagnostic endpoint to confirm the actual PostgreSQL
    database and schema being used by the running ECS application.
    """
    diagnostic = await get_database_diagnostic()
    return DatabaseDiagnosticResponse(**diagnostic)