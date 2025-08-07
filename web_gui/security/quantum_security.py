"""Quantum-inspired security helpers."""

from __future__ import annotations

import logging
import secrets
from typing import Iterable

from secondary_copilot_validator import SecondaryCopilotValidator

logger = logging.getLogger(__name__)


def generate_quantum_token(
    roles: Iterable[str],
    validator: SecondaryCopilotValidator | None = None,
) -> str:
    """Return a random token if ``roles`` contain ``"quantum"``."""

    if "quantum" not in set(roles):
        logger.warning("Quantum token generation denied")
        raise PermissionError("missing quantum role")
    token = secrets.token_hex(16)
    logger.info("Quantum token generated")
    (validator or SecondaryCopilotValidator()).validate_corrections([token])
    return token


__all__ = ["generate_quantum_token"]

