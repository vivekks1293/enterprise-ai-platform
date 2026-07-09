from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.application.identity.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    InactiveUserError,
    UserNotFoundError,
)


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


def register_exception_handlers(
    app: FastAPI,
) -> None:

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request,
        exc: InvalidCredentialsError,
    ):
        return _error_response(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid credentials.",
        )

    @app.exception_handler(InvalidTokenError)
    async def invalid_token_handler(
        request: Request,
        exc: InvalidTokenError,
    ):
        return _error_response(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired access token.",
        )

    @app.exception_handler(InactiveUserError)
    async def inactive_user_handler(
        request: Request,
        exc: InactiveUserError,
    ):
        return _error_response(
            status.HTTP_403_FORBIDDEN,
            "User account is inactive.",
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(
        request: Request,
        exc: UserNotFoundError,
    ):
        return _error_response(
            status.HTTP_404_NOT_FOUND,
            "User not found.",
        )