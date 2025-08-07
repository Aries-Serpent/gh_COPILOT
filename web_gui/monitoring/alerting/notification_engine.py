"""Notification engine for alerts."""

from __future__ import annotations

__all__ = ["send_notification", "route_to_dashboard"]


def send_notification(message: str) -> None:
    """Placeholder notification sender."""
    print(message)


def route_to_dashboard(level: str, message: str) -> None:
    """Placeholder router forwarding alerts to dashboards."""
    print(f"ROUTE[{level.upper()}] {message}")
