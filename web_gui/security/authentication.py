"""Simple role-aware authentication helpers."""

from __future__ import annotations

import logging
from typing import Dict, Iterable

from secondary_copilot_validator import SecondaryCopilotValidator

logger = logging.getLogger(__name__)

UserDB = Dict[str, Dict[str, Iterable[str]]]


def authenticate_user(
    username: str,
    password: str,
    user_db: UserDB,
    required_role: str | None = None,
    validator: SecondaryCopilotValidator | None = None,
) -> bool:
    """Authenticate ``username`` and optionally enforce ``required_role``."""

    record = user_db.get(username)
    if not record or record.get("password") != password:
        logger.warning("Authentication failed for user %s", username)
        result = False
    else:
        roles = set(record.get("roles", []))
        if required_role and required_role not in roles:
            logger.warning("User %s lacks role %s", username, required_role)
            result = False
        else:
            logger.info("User %s authenticated", username)
            result = True

    (validator or SecondaryCopilotValidator()).validate_corrections([str(result)])
    return result


__all__ = ["authenticate_user"]

