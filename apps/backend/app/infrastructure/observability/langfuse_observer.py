from __future__ import annotations

import asyncio
import logging
from contextlib import contextmanager
from collections.abc import Iterator
from typing import Any

from app.core.logging.logger import log_event


logger = logging.getLogger(__name__)


class _NoopGeneration:
    def update(self, **kwargs: Any) -> None:
        return None


class LangfuseObserver:
    """Best-effort infrastructure adapter for Langfuse GenAI observations."""

    def __init__(
        self,
        *,
        client: Any | None = None,
        enabled: bool = False,
        capture_content: bool = False,
    ) -> None:
        self._client = client
        self._enabled = enabled and client is not None
        self._capture_content = capture_content

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def capture_content(self) -> bool:
        return self._capture_content

    @contextmanager
    def start_generation(
        self,
        *,
        provider: str,
        model: str,
        input_content: Any | None = None,
    ) -> Iterator[Any]:
        if not self._enabled:
            yield _NoopGeneration()
            return

        try:
            observation_context = self._client.start_as_current_observation(
                name="rag.llm_generation",
                as_type="generation",
                model=model,
                model_parameters={"provider": provider},
                input=input_content if self._capture_content else None,
            )
            generation = observation_context.__enter__()
        except Exception as exc:
            log_event(
                logger,
                "observability.langfuse_failed",
                stage="generation",
                exception_type=type(exc).__name__,
                error_classification="observation_export",
            )
            yield _NoopGeneration()
            return

        try:
            yield generation
        finally:
            try:
                observation_context.__exit__(None, None, None)
            except Exception as exc:
                log_event(
                    logger,
                    "observability.langfuse_failed",
                    stage="generation_close",
                    exception_type=type(exc).__name__,
                    error_classification="observation_close",
                )

    def update_generation(
        self,
        generation: Any,
        *,
        output: str,
        metadata: dict[str, Any],
        usage_details: dict[str, int] | None = None,
        level: str | None = None,
        status_message: str | None = None,
    ) -> None:
        if not self._enabled:
            return

        try:
            generation.update(
                output=output if self._capture_content else None,
                metadata=metadata,
                usage_details=usage_details,
                level=level,
                status_message=status_message,
            )
        except Exception as exc:
            log_event(
                logger,
                "observability.langfuse_failed",
                stage="generation_update",
                exception_type=type(exc).__name__,
                error_classification="observation_update",
            )

    async def shutdown(self, timeout_seconds: float = 2.0) -> None:
        if not self._enabled:
            return

        try:
            await asyncio.wait_for(
                asyncio.to_thread(self._client.flush),
                timeout=timeout_seconds,
            )
            await asyncio.wait_for(
                asyncio.to_thread(self._client.shutdown),
                timeout=timeout_seconds,
            )
        except Exception as exc:
            log_event(
                logger,
                "observability.langfuse_failed",
                stage="shutdown",
                exception_type=type(exc).__name__,
                error_classification="flush_timeout_or_export",
            )
