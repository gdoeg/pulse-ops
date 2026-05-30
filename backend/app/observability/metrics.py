"""Simple in-memory metrics registry with Prometheus text rendering."""

from collections import Counter
from threading import Lock


class AppMetrics:
    """Track request and error counters for the API process."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._request_counts: Counter[tuple[str, str, int]] = Counter()
        self._request_duration_seconds_total = 0.0
        self._errors_total = 0

    def record_request(
        self,
        *,
        method: str,
        path: str,
        status_code: int,
        duration_seconds: float,
    ) -> None:
        """Record a completed HTTP request."""
        with self._lock:
            self._request_counts[(method, path, status_code)] += 1
            self._request_duration_seconds_total += duration_seconds

    def record_error(self) -> None:
        """Record an unhandled application error."""
        with self._lock:
            self._errors_total += 1

    def render_prometheus(self) -> str:
        """Render metrics in a Prometheus-compatible text format."""
        with self._lock:
            lines = [
                "# HELP pulseops_http_requests_total Total HTTP requests processed.",
                "# TYPE pulseops_http_requests_total counter",
            ]
            for (method, path, status_code), count in sorted(self._request_counts.items()):
                lines.append(
                    "pulseops_http_requests_total"
                    f'{{method="{method}",path="{path}",status_code="{status_code}"}} {count}'
                )

            lines.extend(
                [
                    "# HELP pulseops_http_request_duration_seconds_total Total accumulated request duration.",
                    "# TYPE pulseops_http_request_duration_seconds_total counter",
                    (
                        "pulseops_http_request_duration_seconds_total "
                        f"{self._request_duration_seconds_total:.6f}"
                    ),
                    "# HELP pulseops_http_request_errors_total Total unhandled request errors.",
                    "# TYPE pulseops_http_request_errors_total counter",
                    f"pulseops_http_request_errors_total {self._errors_total}",
                ]
            )

        return "\n".join(lines) + "\n"
