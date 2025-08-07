"""Escalation rules for alerts."""

from __future__ import annotations

from typing import Dict

__all__ = ["get_escalation_level"]


ESCALATION_MAP: Dict[str, str] = {
    "critical": "high",
    "warning": "medium",
    "info": "low",
}


def get_escalation_level(alert_type: str) -> str:
    """Return the escalation level for ``alert_type``."""
    return ESCALATION_MAP.get(alert_type, "low")
