"""Audit logging utilities."""

from __future__ import annotations

import logging
from typing import Iterable

logger = logging.getLogger(__name__)


def log_event(user: str, action: str, roles: Iterable[str]) -> None:
    """Log ``action`` performed by ``user`` if ``roles`` include ``"auditor"``."""

    if "auditor" not in set(roles):
        logger.warning("Audit log denied for user %s", user)
        raise PermissionError("missing auditor role")
    logger.info("AUDIT %s: %s", user, action)


__all__ = ["log_event"]

