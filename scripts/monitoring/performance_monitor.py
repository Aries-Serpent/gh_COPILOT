#!/usr/bin/env python3
"""Performance Monitor

Collects CPU and memory metrics using :mod:`psutil` and exposes them in
Prometheus exposition format via a simple HTTP endpoint.
"""

from __future__ import annotations

import argparse
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict

import psutil

__all__ = [
    "main",
    "collect_cpu_usage",
    "collect_memory_usage",
    "format_prometheus",
]


def collect_cpu_usage() -> float:
    """Return current system-wide CPU usage percentage."""

    return float(psutil.cpu_percent(interval=None))


def collect_memory_usage() -> float:
    """Return current system memory usage percentage."""

    return float(psutil.virtual_memory().percent)


def format_prometheus(metrics: dict[str, float]) -> str:
    """Return ``metrics`` formatted for Prometheus scraping."""

    lines: list[str] = []
    for key, value in metrics.items():
        lines.append(f"# TYPE {key} gauge")
        lines.append(f"{key} {value}")
    return "\n".join(lines) + "\n"


@dataclass
class MonitoringRequest:
    """Contract for performance monitoring input."""

    interval: int


def validate_monitoring_request(request: MonitoringRequest) -> None:
    """Assert that the monitoring request complies with the contract."""

    if request.interval <= 0:
        raise ValueError("interval must be positive")


def main(argv: list[str] | None = None) -> int:
    """Run performance monitoring loop and expose an HTTP endpoint."""

    ap = argparse.ArgumentParser(
        description="Run performance monitor and expose metrics endpoint.",
    )
    ap.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Interval in seconds between samples",
    )
    ap.add_argument("--host", default="0.0.0.0", help="Host for metrics HTTP server")
    ap.add_argument("--port", type=int, default=8000, help="Port for metrics HTTP server")
    ns = ap.parse_args(argv)

    request = MonitoringRequest(interval=ns.interval)
    validate_monitoring_request(request)

    latest_metrics: Dict[str, float] = {}

    def _sampling_loop() -> None:
        while True:
            latest_metrics.update(
                {
                    "cpu_usage_percent": collect_cpu_usage(),
                    "memory_usage_percent": collect_memory_usage(),
                    "timestamp": time.time(),
                }
            )
            time.sleep(request.interval)

    class _MetricsHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
            if self.path != "/metrics":
                self.send_response(404)
                self.end_headers()
                return

            content = format_prometheus(latest_metrics)
            encoded = content.encode()

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, format: str, *args: object) -> None:  # pragma: no cover
            return

    threading.Thread(target=_sampling_loop, daemon=True).start()
    print(f"performance_monitor serving on {ns.host}:{ns.port}, interval={request.interval}s")
    try:
        HTTPServer((ns.host, ns.port), _MetricsHandler).serve_forever()
    except KeyboardInterrupt:
        print("performance_monitor stopped by user")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

