"""Notification engine for alerts.

This module provides simple notification handlers used by the alerting
pipeline. Handlers share a common signature of ``(level, message)`` and
append information to in-memory logs so tests can assert on side effects.

Additional handlers ``send_email`` and ``send_sms`` emulate email/SMS
notifications by recording messages to dedicated logs.
"""

from __future__ import annotations

from typing import List, Tuple

# In-memory logs used for test assertions
NOTIFICATION_LOG: List[str] = []
ROUTE_LOG: List[Tuple[str, str]] = []
EMAIL_LOG: List[str] = []
SMS_LOG: List[str] = []

__all__ = [
    "send_notification",
    "route_to_dashboard",
    "send_email",
    "send_sms",
    "NOTIFICATION_LOG",
    "ROUTE_LOG",
    "EMAIL_LOG",
    "SMS_LOG",
]


def send_notification(level: str, message: str) -> None:
    """Record ``message`` with ``level`` and emit it to stdout."""
    formatted = f"[{level.upper()}] {message}"
    NOTIFICATION_LOG.append(formatted)
    print(formatted)


def route_to_dashboard(level: str, message: str) -> None:
    """Placeholder router forwarding alerts to dashboards."""
    ROUTE_LOG.append((level, message))
    print(f"ROUTE[{level.upper()}] {message}")


def send_email(level: str, message: str) -> None:
    """Record an email alert."""
    formatted = f"EMAIL[{level.upper()}] {message}"
    EMAIL_LOG.append(formatted)
    print(formatted)


def send_sms(level: str, message: str) -> None:
    """Record an SMS alert."""
    formatted = f"SMS[{level.upper()}] {message}"
    SMS_LOG.append(formatted)
    print(formatted)

