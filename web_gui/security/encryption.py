"""Lightweight symmetric encryption helpers with dual-copilot validation."""

from __future__ import annotations

import logging
from base64 import b64decode, b64encode
from itertools import cycle
from typing import ByteString, Iterable

from flask import Flask

from secondary_copilot_validator import SecondaryCopilotValidator

logger = logging.getLogger(__name__)


def init_app(app: Flask) -> None:
    """Ensure ``ENCRYPTION_KEY`` is configured."""

    app.config.setdefault("ENCRYPTION_KEY", b"supersecretkey")


def _xor(data: ByteString, key: ByteString) -> bytes:
    return bytes(a ^ b for a, b in zip(data, cycle(key)))


def encrypt(
    data: bytes,
    key: bytes,
    roles: Iterable[str],
    validator: SecondaryCopilotValidator | None = None,
) -> str:
    """Encrypt *data* using XOR and return a base64 token.

    ``roles`` must include ``"crypto"`` to proceed.
    """

    if "crypto" not in set(roles):
        logger.warning("Encryption denied, missing 'crypto' role")
        raise PermissionError("missing crypto role")
    token = b64encode(_xor(data, key)).decode("ascii")
    logger.info("Data encrypted with XOR")
    (validator or SecondaryCopilotValidator()).validate_corrections([token])
    return token


def decrypt(
    token: str,
    key: bytes,
    roles: Iterable[str],
    validator: SecondaryCopilotValidator | None = None,
) -> bytes:
    """Decrypt *token* produced by :func:`encrypt`.

    ``roles`` must include ``"crypto"`` to proceed.
    """

    if "crypto" not in set(roles):
        logger.warning("Decryption denied, missing 'crypto' role")
        raise PermissionError("missing crypto role")
    data = _xor(b64decode(token.encode("ascii")), key)
    logger.info("Data decrypted with XOR")
    (validator or SecondaryCopilotValidator()).validate_corrections([data.hex()])
    return data


__all__ = ["init_app", "encrypt", "decrypt"]

