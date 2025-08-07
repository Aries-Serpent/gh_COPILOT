"""Request audit logging utilities."""

from __future__ import annotations

from flask import Flask, Response, request

from secondary_copilot_validator import SecondaryCopilotValidator

logger = logging.getLogger(__name__)

def init_app(app: Flask) -> None:
    """Log each request and response status code when enabled."""
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
    logger.info("AUDIT %s: %s", user, action)
    (validator or SecondaryCopilotValidator()).validate_corrections([f"{user}:{action}"])


__all__ = ["init_app"]
