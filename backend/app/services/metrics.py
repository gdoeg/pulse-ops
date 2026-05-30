"""Business logic for metrics exposition."""

from app.observability.metrics import AppMetrics


class MetricsService:
    """Render observability metrics for scraping systems."""

    def __init__(self, metrics: AppMetrics) -> None:
        self._metrics = metrics

    def render(self) -> str:
        """Return metrics in Prometheus exposition format."""
        return self._metrics.render_prometheus()
