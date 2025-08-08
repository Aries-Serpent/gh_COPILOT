"""Simple alert manager for web GUI monitoring."""

from __future__ import annotations

from typing import Callable, Iterable, Optional

from .escalation_rules import get_escalation_level, get_pipeline

__all__ = ["trigger_alert"]


def trigger_alert(
    message: str,
    alert_type: str = "info",
    pipeline: Optional[Iterable[Callable[[str, str], None]]] = None,
) -> str:
    """Send an alert through a severity-specific pipeline.

    Parameters
    ----------
    message:
        Human readable alert message.
    alert_type:
        Category of alert (``info``, ``warning``, ``critical``).
    pipeline:
        Optional iterable of handlers. Each handler receives ``(level, message)``.
        When ``None`` the default pipeline for ``alert_type`` is used.
    """
    level = get_escalation_level(alert_type)
    handlers = list(pipeline) if pipeline is not None else get_pipeline(alert_type)
    for handler in handlers:
        handler(level, message)
    return level
