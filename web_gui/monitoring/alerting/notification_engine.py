"""Notification engine for alerts.

This module provides simple notification handlers used by the alerting
pipeline. Handlers share a common signature of ``(level, message)`` and
append information to in-memory logs so tests can assert on side effects.
"""

from __future__ import annotations

from typing import List

NOTIFICATION_LOG: List[str] = []

__all__ = ["send_notification", "route_to_dashboard", "NOTIFICATION_LOG"]

NOTIFICATION_LOG: List[str] = []

# In-memory logs used for test assertions
NOTIFICATION_LOG: List[str] = []
ROUTE_LOG: List[Tuple[str, str]] = []


def send_notification(level: str, message: str) -> None:
    """Record ``message`` with ``level`` and emit it to stdout."""
    formatted = f"[{level.upper()}] {message}"
    NOTIFICATION_LOG.append(formatted)
    print(formatted)


def route_to_dashboard(level: str, message: str) -> None:
    """Placeholder router forwarding alerts to dashboards."""
    ROUTE_LOG.append((level, message))
    print(f"ROUTE[{level.upper()}] {message}")

