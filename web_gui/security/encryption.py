"""Lightweight symmetric encryption helpers."""

from __future__ import annotations

from base64 import b64decode, b64encode
from itertools import cycle
from typing import ByteString

from flask import Flask


def init_app(app: Flask) -> None:
    """Ensure ``ENCRYPTION_KEY`` is configured."""
    app.config.setdefault("ENCRYPTION_KEY", b"supersecretkey")


def _xor(data: ByteString, key: ByteString) -> bytes:
    return bytes(a ^ b for a, b in zip(data, cycle(key)))


def encrypt(data: bytes, key: bytes) -> str:
    """Encrypt *data* using a repeated-key XOR and return base64 text."""
    return b64encode(_xor(data, key)).decode("ascii")


def decrypt(token: str, key: bytes) -> bytes:
    """Decrypt *token* produced by :func:`encrypt`."""
    return _xor(b64decode(token.encode("ascii")), key)


__all__ = ["init_app", "encrypt", "decrypt"]
