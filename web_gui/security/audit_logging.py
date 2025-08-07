"""Request audit logging utilities."""

from __future__ import annotations

import logging
from typing import Iterable

from flask import Flask

from secondary_copilot_validator import SecondaryCopilotValidator

logger = logging.getLogger(__name__)


def init_app(app: Flask) -> None:
    """Configure audit logging for *app*."""

    app.config.setdefault("AUDIT_LOGGING", False)


def log_event(
    user: str,
    action: str,
    roles: Iterable[str],
    validator: SecondaryCopilotValidator | None = None,
) -> None:
    """Log ``action`` performed by ``user`` if ``roles`` include ``"auditor"``."""

    if "auditor" not in set(roles):
        logger.warning("Audit log denied for user %s", user)
        raise PermissionError("missing auditor role")
    message = f"AUDIT {user}: {action}"
    logger.info(message)
    (validator or SecondaryCopilotValidator()).validate_corrections([message])


__all__ = ["init_app", "log_event"]
