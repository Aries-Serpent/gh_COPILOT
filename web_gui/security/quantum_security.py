"""Quantum-inspired security helpers."""

from __future__ import annotations

import logging
import secrets
from typing import Iterable

logger = logging.getLogger(__name__)


def generate_quantum_token(roles: Iterable[str]) -> str:
    """Return a random token if ``roles`` contain ``"quantum"``."""

    if "quantum" not in set(roles):
        logger.warning("Quantum token generation denied")
        raise PermissionError("missing quantum role")
    token = secrets.token_hex(16)
    logger.info("Quantum token generated")
    return token


__all__ = ["generate_quantum_token"]

