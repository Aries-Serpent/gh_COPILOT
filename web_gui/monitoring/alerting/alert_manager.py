"""Simple alert manager for web GUI monitoring."""

from __future__ import annotations

from typing import Callable, Optional

from .notification_engine import route_to_dashboard, send_notification
from .escalation_rules import get_escalation_level

__all__ = ["trigger_alert"]


def trigger_alert(
    message: str,
    alert_type: str = "info",
    notifier: Callable[[str], None] = send_notification,
    dashboard_router: Optional[Callable[[str, str], None]] = None,
) -> str:
    """Send an alert and optionally route to dashboards.

    Parameters
    ----------
    message:
        Human readable alert message.
    alert_type:
        Category of alert (``info``, ``warning``, ``critical``).
    notifier:
        Callback used to deliver the formatted alert.
    dashboard_router:
        Optional callback receiving the escalation level and original
        message for dashboard routing.
    """
    level = get_escalation_level(alert_type)
    formatted = f"[{level.upper()}] {message}"
    notifier(formatted)
    if dashboard_router is None:
        dashboard_router = route_to_dashboard
    dashboard_router(level, message)
    return level
