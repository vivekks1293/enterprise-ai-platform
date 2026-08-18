import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.application.identity.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    InactiveUserError,
    UserNotFoundError,
)

from app.delivery.api.schemas.common import ErrorResponse

from app.application.conversation.exceptions import (
    ConversationNotFoundError,
)
from app.core.logging.logger import log_event


logger = logging.getLogger(__name__)


def _error_response(
    status_code: int,
    message: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": message,
        },
    )


def _log_application_exception(exc: Exception, error_code: str) -> None:
    log_event(
        logger,
        "request.failed",
        stage="http",
        exception_type=type(exc).__name__,
        error_code=error_code,
    )


def register_exception_handlers(
    app: FastAPI,
) -> None:

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request,
        exc: InvalidCredentialsError,
    ):
        _log_application_exception(exc, "invalid_credentials")
        return _error_response(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid credentials.",
        )

    @app.exception_handler(InvalidTokenError)
    async def invalid_token_handler(
        request: Request,
        exc: InvalidTokenError,
    ):
        _log_application_exception(exc, "invalid_token")
        return _error_response(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired access token.",
        )

    @app.exception_handler(InactiveUserError)
    async def inactive_user_handler(
        request: Request,
        exc: InactiveUserError,
    ):
        _log_application_exception(exc, "inactive_user")
        return _error_response(
            status.HTTP_403_FORBIDDEN,
            "User account is inactive.",
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(
        request: Request,
        exc: UserNotFoundError,
    ):
        _log_application_exception(exc, "user_not_found")
        return _error_response(
            status.HTTP_404_NOT_FOUND,
            "User not found.",
        )
    
    @app.exception_handler(ConversationNotFoundError)
    async def conversation_not_found_handler(
        request: Request,
        exc: ConversationNotFoundError,
    ):
        _log_application_exception(exc, "conversation_not_found")
        response = ErrorResponse(
            error="ConversationNotFound",
            message=str(exc),
        )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response.model_dump(mode="json"),
        )