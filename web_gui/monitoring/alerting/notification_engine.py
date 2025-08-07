"""Notification engine for alerts."""

from __future__ import annotations

from typing import List

__all__ = ["send_notification", "NOTIFICATION_LOG"]

NOTIFICATION_LOG: List[str] = []


def send_notification(message: str) -> None:
    """Record ``message`` and emit it to stdout."""
    NOTIFICATION_LOG.append(message)
    print(message)
