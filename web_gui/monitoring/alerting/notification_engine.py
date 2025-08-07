"""Notification engine for alerts."""

from __future__ import annotations

from typing import List

NOTIFICATION_LOG: List[str] = []

__all__ = ["send_notification", "route_to_dashboard", "NOTIFICATION_LOG"]


def send_notification(message: str) -> None:
    """Record ``message`` and emit it to stdout."""
    NOTIFICATION_LOG.append(message)
    print(message)


def route_to_dashboard(level: str, message: str) -> None:
    """Placeholder router forwarding alerts to dashboards."""
    print(f"ROUTE[{level.upper()}] {message}")
