from app.application.common.ports.metrics_recorder import MetricsRecorder
from app.infrastructure.observability.in_memory_metrics_recorder import (
    InMemoryMetricsRecorder,
)


_metrics_recorder = InMemoryMetricsRecorder()


def get_metrics_recorder() -> MetricsRecorder:
    """Returns the process-wide operational metrics recorder."""

    return _metrics_recorder