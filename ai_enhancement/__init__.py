"""AI enhancement modules for advanced features."""
from __future__ import annotations

import logging
from typing import Any, Dict

__all__ = [
    "cognitive_computing",
    "nlp",
    "maintenance",
    "ecosystem_integration",
]


def _send_to_gui(event: str, payload: Dict[str, Any]) -> None:
    """Best-effort helper to forward results to the web GUI.

    The implementation attempts to leverage the :mod:`web_gui_integration_system`
    module which wires data into the Flask dashboard.  Importing that module at
    runtime can fail if optional dependencies (like Flask) are missing.  To keep
    unit tests lightweight and avoid hard failures, any import or runtime error
    is silently converted into a log message.
    """

    try:  # pragma: no cover - best effort integration
        from web_gui_integration_system import WebGUIIntegrationSystem

        system = WebGUIIntegrationSystem()
        system.logger.info("web-gui event %s: %s", event, payload)
    except Exception:  # pragma: no cover - integration is optional
        logging.getLogger(__name__).info("web-gui event %s: %s", event, payload)

