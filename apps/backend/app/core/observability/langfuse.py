from __future__ import annotations

import logging

from langfuse import Langfuse
from opentelemetry import trace

from app.core.config.settings import settings
from app.core.logging.logger import log_event
from app.infrastructure.observability.langfuse_observer import LangfuseObserver


logger = logging.getLogger(__name__)
_observer: LangfuseObserver | None = None


def configure_langfuse() -> LangfuseObserver:
    """Creates an optional Langfuse observer without blocking app startup."""

    global _observer

    if _observer is not None:
        return _observer

    if not settings.langfuse_enabled:
        _observer = LangfuseObserver()
        return _observer

    if not all(
        (
            settings.langfuse_public_key,
            settings.langfuse_secret_key,
            settings.langfuse_base_url,
        )
    ):
        log_event(
            logger,
            "observability.langfuse_failed",
            stage="initialization",
            exception_type="MissingConfiguration",
            error_classification="configuration_missing",
        )
        _observer = LangfuseObserver()
        return _observer

    try:
        client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            base_url=settings.langfuse_base_url,
            environment=settings.environment,
            tracing_enabled=True,
            tracer_provider=trace.get_tracer_provider(),
        )
        _observer = LangfuseObserver(
            client=client,
            enabled=True,
            capture_content=settings.langfuse_capture_content,
        )
    except Exception as exc:
        log_event(
            logger,
            "observability.langfuse_failed",
            stage="initialization",
            exception_type=type(exc).__name__,
            error_classification="client_initialization",
        )
        _observer = LangfuseObserver()

    return _observer


def get_langfuse_observer() -> LangfuseObserver:
    return configure_langfuse()
