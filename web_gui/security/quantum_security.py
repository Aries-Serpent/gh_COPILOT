"""Quantum-inspired security helpers."""

from __future__ import annotations

from flask import Flask

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

def generate_token(length: int) -> str:
    """Return a random hexadecimal token generated using quantum-safe methods."""
    return quantum_crypto.generate_quantum_safe_key(length).hex()


__all__ = ["init_app", "generate_token"]
