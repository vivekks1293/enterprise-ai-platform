import asyncio
import logging
from collections.abc import Awaitable, Callable
from time import perf_counter
from uuid import UUID, uuid4

import structlog
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging.logger import log_event, request_id_context


logger = logging.getLogger(__name__)


class RequestCorrelationMiddleware:
    """Correlates all logs and response data for one HTTP request."""

    _REQUEST_ID_HEADER = b"x-request-id"

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        request_id = self._resolve_request_id(scope)
        scope.setdefault("state", {})["request_id"] = request_id
        request_token = request_id_context.set(request_id)
        structlog_tokens = structlog.contextvars.bind_contextvars(
            request_id=request_id,
        )
        started_at = perf_counter()
        status_code: int | None = None
        error_type: str | None = None

        log_event(
            logger,
            "request.started",
            method=scope["method"],
            path=scope["path"],
        )

        async def send_with_request_id(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = list(message.get("headers", []))
                headers.append((self._REQUEST_ID_HEADER, request_id.encode("ascii")))
                message = {**message, "headers": headers}

            await send(message)

        try:
            await self._app(scope, receive, send_with_request_id)
        except BaseException as exc:
            error_type = type(exc).__name__
            raise
        finally:
            log_event(
                logger,
                "request.completed",
                method=scope["method"],
                path=scope["path"],
                status_code=status_code,
                duration_ms=round((perf_counter() - started_at) * 1000, 2),
                outcome=(
                    "cancelled"
                    if error_type == asyncio.CancelledError.__name__
                    else "error"
                    if error_type is not None
                    else "completed"
                ),
                error_type=error_type,
            )
            structlog.contextvars.reset_contextvars(**structlog_tokens)
            request_id_context.reset(request_token)

    @classmethod
    def _resolve_request_id(cls, scope: Scope) -> str:
        for name, value in scope.get("headers", []):
            if name.lower() != cls._REQUEST_ID_HEADER:
                continue

            try:
                request_id = value.decode("ascii")
                UUID(request_id)
            except (UnicodeDecodeError, ValueError):
                break
            return request_id

        return str(uuid4())