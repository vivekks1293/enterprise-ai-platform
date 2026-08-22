from opentelemetry import trace
from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_NAME,
    SERVICE_VERSION,
    Resource,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.trace import Span, Status, StatusCode

from app.core.config.settings import settings


tracer = trace.get_tracer("enterprise-ai-platform")


def mark_span_error(span: Span, exc: Exception) -> None:
    """Marks a span failed without recording potentially sensitive messages."""

    span.set_status(Status(StatusCode.ERROR, type(exc).__name__))
    span.add_event(
        "exception",
        attributes={"exception.type": type(exc).__name__},
    )


def configure_opentelemetry() -> TracerProvider:
    """Configures tracing without requiring a telemetry backend."""

    resource = Resource.create(
        {
            SERVICE_NAME: settings.app_name,
            SERVICE_VERSION: settings.app_version,
            DEPLOYMENT_ENVIRONMENT: settings.environment,
        }
    )
    sampler = TraceIdRatioBased(settings.otel_sampling_ratio)
    provider = TracerProvider(resource=resource, sampler=sampler)

    if settings.otel_console_exporter:
        provider.add_span_processor(
            BatchSpanProcessor(ConsoleSpanExporter())
        )

    trace.set_tracer_provider(provider)
    return provider