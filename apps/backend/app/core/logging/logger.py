import logging
from contextvars import ContextVar
from typing import Any

import structlog


request_id_context: ContextVar[str | None] = ContextVar(
    "request_id",
    default=None,
)
_STANDARD_LOG_RECORD_FIELDS = set(logging.makeLogRecord({}).__dict__)


class StructuredFormatter(logging.Formatter):
    """Renders safe structured fields as readable key-value log output."""

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _STANDARD_LOG_RECORD_FIELDS
        }
        if not fields:
            return message

        rendered_fields = " ".join(
            f"{key}={value!r}"
            for key, value in sorted(fields.items())
        )
        return f"{message} {rendered_fields}"


class RequestContextFilter(logging.Filter):
    """Adds request-local correlation metadata to standard log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = request_id_context.get()
        return True


def log_event(
    logger: logging.Logger,
    event: str,
    **fields: Any,
) -> None:
    """Emits a structured event without placing sensitive values in the message."""

    logger.info(
        event,
        extra={
            "event": event,
            "request_id": request_id_context.get(),
            **fields,
        },
    )


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
    )

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(StructuredFormatter())
        if not any(
            isinstance(log_filter, RequestContextFilter)
            for log_filter in handler.filters
        ):
            handler.addFilter(RequestContextFilter())

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


logger = structlog.get_logger()