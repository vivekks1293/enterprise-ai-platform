from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.application.conversation.exceptions import (
    ConversationNotFoundError,
)
from app.delivery.api.schemas.common import ErrorResponse

async def conversation_not_found_handler(
    request: Request,
    exc: ConversationNotFoundError,
):
    response = ErrorResponse(
        error="ConversationNotFound",
        message=str(exc),
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=response.model_dump(mode="json"),
    )

def register_exception_handlers(
    app: FastAPI,
) -> None:

    app.add_exception_handler(
        ConversationNotFoundError,
        conversation_not_found_handler,
    )