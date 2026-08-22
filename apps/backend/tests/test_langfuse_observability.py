import asyncio
from contextlib import contextmanager
from uuid import UUID

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from app.infrastructure.observability.langfuse_observer import LangfuseObserver
from app.core.observability import langfuse as langfuse_configuration


class FakeGeneration:
    def __init__(self) -> None:
        self.updates: list[dict] = []

    def update(self, **kwargs) -> None:
        self.updates.append(kwargs)


class FakeClient:
    def __init__(self) -> None:
        self.generation = FakeGeneration()
        self.active_trace_id: int | None = None
        self.flush_count = 0
        self.shutdown_count = 0

    @contextmanager
    def start_as_current_observation(self, **kwargs):
        self.arguments = kwargs
        self.active_trace_id = trace.get_current_span().get_span_context().trace_id
        yield self.generation

    def flush(self) -> None:
        self.flush_count += 1

    def shutdown(self) -> None:
        self.shutdown_count += 1


class FailingClient(FakeClient):
    @contextmanager
    def start_as_current_observation(self, **kwargs):
        raise RuntimeError("telemetry unavailable")
        yield self.generation

    def flush(self) -> None:
        raise RuntimeError("flush unavailable")


@pytest.fixture
def tracer_provider():
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider, exporter


def test_disabled_observer_is_a_noop():
    observer = LangfuseObserver()

    with observer.start_generation(
        provider="OpenAIChatProvider",
        model="gpt-4.1-mini",
    ) as generation:
        generation.update(output="secret")

    assert observer.enabled is False
    assert observer.capture_content is False


def test_generation_uses_current_trace_and_safe_metadata(tracer_provider):
    provider, exporter = tracer_provider
    client = FakeClient()
    observer = LangfuseObserver(
        client=client,
        enabled=True,
        capture_content=False,
    )
    tracer = provider.get_tracer("test")

    with tracer.start_as_current_span("rag.llm_generation") as parent:
        with observer.start_generation(
            provider="OpenAIChatProvider",
            model="gpt-4.1-mini",
            input_content=[{"role": "user", "content": "private prompt"}],
        ) as generation:
            observer.update_generation(
                generation,
                output="private response",
                metadata={
                    "duration_ms": 12.5,
                    "outcome": "success",
                },
            )

    assert client.active_trace_id == parent.get_span_context().trace_id
    assert client.arguments["model"] == "gpt-4.1-mini"
    assert client.arguments["input"] is None
    assert client.generation.updates[0]["output"] is None
    assert client.generation.updates[0]["metadata"]["outcome"] == "success"
    assert "private prompt" not in str(client.generation.updates)
    assert "private response" not in str(client.generation.updates)
    assert len(exporter.get_finished_spans()) == 1


def test_content_capture_is_explicit_and_usage_is_preserved():
    client = FakeClient()
    observer = LangfuseObserver(
        client=client,
        enabled=True,
        capture_content=True,
    )

    with observer.start_generation(
        provider="OpenAIChatProvider",
        model="gpt-4.1-mini",
        input_content=[{"role": "user", "content": "development prompt"}],
    ) as generation:
        observer.update_generation(
            generation,
            output="development response",
            metadata={"outcome": "success"},
            usage_details={"input": 10, "output": 4, "total": 14},
        )

    assert client.arguments["input"] == [
        {"role": "user", "content": "development prompt"}
    ]
    assert client.generation.updates[0]["output"] == "development response"
    assert client.generation.updates[0]["usage_details"] == {
        "input": 10,
        "output": 4,
        "total": 14,
    }


def test_observer_failure_does_not_escape_application():
    observer = LangfuseObserver(
        client=FailingClient(),
        enabled=True,
        capture_content=False,
    )

    with observer.start_generation(
        provider="OpenAIChatProvider",
        model="gpt-4.1-mini",
    ) as generation:
        generation.update(output="application continues")

    assert observer.enabled is True


def test_shutdown_is_bounded_and_best_effort():
    client = FakeClient()
    observer = LangfuseObserver(client=client, enabled=True)

    asyncio.run(observer.shutdown(timeout_seconds=1))

    assert client.flush_count == 1
    assert client.shutdown_count == 1


def test_shutdown_failures_do_not_escape_application():
    observer = LangfuseObserver(
        client=FailingClient(),
        enabled=True,
    )

    asyncio.run(observer.shutdown(timeout_seconds=1))


def test_configuration_disabled_does_not_create_client(monkeypatch):
    monkeypatch.setattr(langfuse_configuration, "_observer", None)
    monkeypatch.setattr(langfuse_configuration.settings, "langfuse_enabled", False)

    observer = langfuse_configuration.configure_langfuse()

    assert observer.enabled is False


def test_enabled_configuration_with_missing_credentials_falls_back_safely(monkeypatch):
    monkeypatch.setattr(langfuse_configuration, "_observer", None)
    monkeypatch.setattr(langfuse_configuration.settings, "langfuse_enabled", True)
    monkeypatch.setattr(langfuse_configuration.settings, "langfuse_public_key", None)
    monkeypatch.setattr(langfuse_configuration.settings, "langfuse_secret_key", None)
    monkeypatch.setattr(langfuse_configuration.settings, "langfuse_base_url", None)

    observer = langfuse_configuration.configure_langfuse()

    assert observer.enabled is False
