"""Simple alert manager for web GUI monitoring."""

from __future__ import annotations

from typing import Callable

from .notification_engine import send_notification
from .escalation_rules import get_escalation_level

__all__ = ["trigger_alert"]


def trigger_alert(message: str, alert_type: str = "info", notifier: Callable[[str], None] = send_notification) -> str:
    """Send an alert notification and return its escalation level."""
    level = get_escalation_level(alert_type)
    notifier(f"[{level.upper()}] {message}")
    return level
