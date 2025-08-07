"""Authorization helpers with role checks."""

from __future__ import annotations

import logging
from typing import Iterable

from secondary_copilot_validator import SecondaryCopilotValidator

logger = logging.getLogger(__name__)


def has_role(
    user_roles: Iterable[str],
    required_role: str,
    validator: SecondaryCopilotValidator | None = None,
) -> bool:
    """Return ``True`` if ``required_role`` is present in ``user_roles``."""

    allowed = required_role in set(user_roles)
    if not allowed:
        logger.warning("Missing required role: %s", required_role)
    (validator or SecondaryCopilotValidator()).validate_corrections([str(allowed)])
    return allowed


__all__ = ["has_role"]

