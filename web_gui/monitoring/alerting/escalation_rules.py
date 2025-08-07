"""Escalation rules for alerts."""

from __future__ import annotations

from typing import Callable, Dict, List

from .notification_engine import route_to_dashboard, send_notification

__all__ = ["get_escalation_level", "get_pipeline"]


ESCALATION_MAP: Dict[str, str] = {
    "critical": "high",
    "warning": "medium",
    "info": "low",
}

PIPELINES: Dict[str, List[Callable[[str, str], None]]] = {
    "critical": [send_notification, route_to_dashboard],
    "warning": [send_notification],
    "info": [send_notification],
}


def get_escalation_level(alert_type: str) -> str:
    """Return the escalation level for ``alert_type``."""
    return ESCALATION_MAP.get(alert_type, "low")


def get_pipeline(alert_type: str) -> List[Callable[[str, str], None]]:
    """Return the handler pipeline for ``alert_type``."""
    return PIPELINES.get(alert_type, [send_notification])
