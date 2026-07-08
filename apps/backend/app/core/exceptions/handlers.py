from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions.models import ErrorResponse
from app.core.logging.logger import logger


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ):
        logger.exception(
            "Unhandled exception",
            path=str(request.url),
        )

        response = ErrorResponse(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred.",
        )

        return JSONResponse(
            status_code=500,
            content=response.model_dump(),
        )