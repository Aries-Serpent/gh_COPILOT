"""Quantum-inspired security helpers."""

from __future__ import annotations

import logging
import secrets
from typing import Iterable

from flask import Flask

from secondary_copilot_validator import SecondaryCopilotValidator

logger = logging.getLogger(__name__)


def init_app(app: Flask) -> None:
    """Initialize quantum security configuration."""

    app.config.setdefault("QUANTUM_TOKEN_BYTES", 16)


def generate_quantum_token(
    roles: Iterable[str],
    length: int | None = None,
    validator: SecondaryCopilotValidator | None = None,
) -> str:
    """Return a random hexadecimal token if ``roles`` contain ``"quantum"``."""

    if "quantum" not in set(roles):
        logger.warning("Quantum token generation denied")
        raise PermissionError("missing quantum role")
    size = length or 16
    token = secrets.token_hex(size)
    logger.info("Quantum token generated")
    (validator or SecondaryCopilotValidator()).validate_corrections([token])
    return token


__all__ = ["init_app", "generate_quantum_token"]
