from collections import defaultdict
from collections.abc import Mapping
from threading import Lock

from app.application.common.ports.metrics_recorder import (
    MetricLabels,
    MetricsRecorder,
)


class InMemoryMetricsRecorder(MetricsRecorder):
    """Thread-safe development and test metrics recorder."""

    _FORBIDDEN_LABELS = frozenset(
        {
            "request_id",
            "user_id",
            "owner_id",
            "conversation_id",
            "document_id",
            "chunk_id",
            "query",
            "prompt",
        }
    )

    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: dict[tuple[str, tuple[tuple[str, str], ...]], int] = (
            defaultdict(int)
        )
        self._observations: dict[
            tuple[str, tuple[tuple[str, str], ...]], list[float]
        ] = defaultdict(list)

    def increment(
        self,
        name: str,
        *,
        labels: MetricLabels | None = None,
        value: int = 1,
    ) -> None:
        key = (name, self._normalize_labels(labels))
        with self._lock:
            self._counters[key] += value

    def observe(
        self,
        name: str,
        value: float,
        *,
        labels: MetricLabels | None = None,
    ) -> None:
        key = (name, self._normalize_labels(labels))
        with self._lock:
            self._observations[key].append(value)

    def counter_value(
        self,
        name: str,
        *,
        labels: MetricLabels | None = None,
    ) -> int:
        key = (name, self._normalize_labels(labels))
        with self._lock:
            return self._counters[key]

    def observations(
        self,
        name: str,
        *,
        labels: MetricLabels | None = None,
    ) -> list[float]:
        key = (name, self._normalize_labels(labels))
        with self._lock:
            return list(self._observations[key])

    @classmethod
    def _normalize_labels(
        cls,
        labels: MetricLabels | None,
    ) -> tuple[tuple[str, str], ...]:
        if labels is None:
            return ()

        forbidden_labels = cls._FORBIDDEN_LABELS & set(labels)
        if forbidden_labels:
            forbidden = ", ".join(sorted(forbidden_labels))
            raise ValueError(f"High-cardinality metric labels are not allowed: {forbidden}")

        return tuple(sorted((str(key), str(value)) for key, value in labels.items()))