"""Minimal encryption utilities with role enforcement."""

from __future__ import annotations

import logging
from typing import Iterable

from secondary_copilot_validator import SecondaryCopilotValidator

logger = logging.getLogger(__name__)


def xor_encrypt(
    data: bytes,
    key: int,
    roles: Iterable[str],
    validator: SecondaryCopilotValidator | None = None,
) -> bytes:
    """XOR ``data`` with ``key`` if ``roles`` contain ``"crypto"``."""

    if "crypto" not in set(roles):
        logger.warning("Encryption denied, missing 'crypto' role")
        raise PermissionError("missing crypto role")
    logger.info("Data encrypted with XOR")
    result = bytes(b ^ key for b in data)
    (validator or SecondaryCopilotValidator()).validate_corrections([result.hex()])
    return result


def xor_decrypt(
    data: bytes,
    key: int,
    roles: Iterable[str],
    validator: SecondaryCopilotValidator | None = None,
) -> bytes:
    """Decrypt ``data`` using the same XOR operation."""

    return xor_encrypt(data, key, roles, validator)


__all__ = ["xor_encrypt", "xor_decrypt"]

