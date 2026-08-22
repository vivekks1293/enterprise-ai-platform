import asyncio
import logging
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from app.application.common.ports.metrics_recorder import MetricsRecorder
from app.core.config.settings import settings
from app.core.logging.logger import log_event, request_id_context
from app.core.middleware.request_correlation import RequestCorrelationMiddleware
from app.core.telemetry.opentelemetry import configure_opentelemetry


REQUEST_ID = "11111111-1111-1111-1111-111111111111"


def create_traced_app(exporter: InMemorySpanExporter) -> FastAPI:
    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": settings.app_name,
                "service.version": settings.app_version,
                "deployment.environment": settings.environment,
            }
        )
    )
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    app = FastAPI()
    app.add_middleware(RequestCorrelationMiddleware)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)

    @app.get("/inspect")
    async def inspect(request: Request):
        span_context = trace.get_current_span().get_span_context()
        log_event(logging.getLogger(__name__), "otel.inspected")
        return {
            "request_id": request.state.request_id,
            "trace_id": format(span_context.trace_id, "032x"),
            "span_id": format(span_context.span_id, "016x"),
        }

    @app.get("/stream")
    async def stream():
        async def events():
            yield "first\n"
            await asyncio.sleep(0)
            yield "last\n"

        return StreamingResponse(events(), media_type="text/plain")

    @app.get("/failure")
    async def failure():
        raise RuntimeError("provider failure")

    return app


def test_tracer_provider_initializes_with_service_metadata():
    provider = configure_opentelemetry()

    assert isinstance(provider, TracerProvider)
    assert provider.resource.attributes["service.name"] == settings.app_name
    assert provider.resource.attributes["service.version"] == settings.app_version
    assert provider.resource.attributes["deployment.environment"] == settings.environment


def test_fastapi_span_contains_request_ids_and_structured_logs(caplog):
    caplog.set_level(logging.INFO)
    exporter = InMemorySpanExporter()
    client = TestClient(create_traced_app(exporter))

    response = client.get("/inspect", headers={"X-Request-ID": REQUEST_ID})
    payload = response.json()

    assert payload["request_id"] == REQUEST_ID
    assert payload["trace_id"] != "0" * 32
    assert payload["span_id"] != "0" * 16
    spans = [
        span
        for span in exporter.get_finished_spans()
        if span.name == "GET /inspect"
    ]
    assert len(spans) == 1
    assert spans[0].resource.attributes["service.name"] == settings.app_name
    records = [record for record in caplog.records if record.getMessage() == "otel.inspected"]
    assert records[0].request_id == REQUEST_ID
    assert records[0].trace_id == payload["trace_id"]
    assert records[0].span_id == payload["span_id"]


def test_sse_http_span_finishes_after_stream_body_is_consumed():
    exporter = InMemorySpanExporter()
    client = TestClient(create_traced_app(exporter))

    response = client.get("/stream", headers={"X-Request-ID": REQUEST_ID})

    assert response.text == "first\nlast\n"
    spans = [
        span
        for span in exporter.get_finished_spans()
        if span.name == "GET /stream"
    ]
    assert len(spans) == 1
    assert spans[0].end_time >= spans[0].start_time


def test_failed_request_closes_http_span():
    exporter = InMemorySpanExporter()
    client = TestClient(
        create_traced_app(exporter),
        raise_server_exceptions=False,
    )

    response = client.get("/failure", headers={"X-Request-ID": REQUEST_ID})

    assert response.status_code == 500
    assert len(
        [
            span
            for span in exporter.get_finished_spans()
            if span.name == "GET /failure"
        ]
    ) == 1


def test_request_context_is_absent_outside_active_span():
    request_token = request_id_context.set(REQUEST_ID)
    try:
        span_context = trace.get_current_span().get_span_context()
        assert not span_context.is_valid
    finally:
        request_id_context.reset(request_token)


def test_metrics_abstraction_is_independent_of_tracing():
    assert isinstance(MetricsRecorder, type)
    provider = configure_opentelemetry()
    assert provider is not None