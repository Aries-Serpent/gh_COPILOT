"""Basic token-based authentication utilities."""

from __future__ import annotations

import logging
from typing import Mapping

from flask import Flask

from secondary_copilot_validator import SecondaryCopilotValidator

logger = logging.getLogger(__name__)

UserDB = Mapping[str, Mapping[str, object]]


def init_app(app: Flask) -> None:
    """Configure authentication defaults for *app*."""

    app.config.setdefault("AUTH_REQUIRED", False)
    app.config.setdefault("AUTH_TOKEN", "")


def authenticate_user(
    username: str,
    password: str,
    user_db: UserDB,
    required_role: str | None = None,
    validator: SecondaryCopilotValidator | None = None,
) -> bool:
    """Return ``True`` if credentials are valid and ``required_role`` matches."""

    record = user_db.get(username)
    if not record or record.get("password") != password:
        logger.warning("Authentication failed for user %s", username)
        result = False
    else:
        roles = set(record.get("roles", []))
        if required_role and required_role not in roles:
            logger.warning("User %s lacks required role %s", username, required_role)
            result = False
        else:
            logger.info("User %s authenticated", username)
            result = True

    (validator or SecondaryCopilotValidator()).validate_corrections([str(result)])
    return result


__all__ = ["init_app", "authenticate_user"]
