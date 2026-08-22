from abc import ABC, abstractmethod
from collections.abc import Mapping


MetricLabels = Mapping[str, str]


class MetricsRecorder(ABC):
    """Provider-agnostic application metrics boundary."""

    @abstractmethod
    def increment(
        self,
        name: str,
        *,
        labels: MetricLabels | None = None,
        value: int = 1,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def observe(
        self,
        name: str,
        value: float,
        *,
        labels: MetricLabels | None = None,
    ) -> None:
        raise NotImplementedError


class NullMetricsRecorder(MetricsRecorder):
    """Default recorder used where metrics collection is not configured."""

    def increment(
        self,
        name: str,
        *,
        labels: MetricLabels | None = None,
        value: int = 1,
    ) -> None:
        return None

    def observe(
        self,
        name: str,
        value: float,
        *,
        labels: MetricLabels | None = None,
    ) -> None:
        return None