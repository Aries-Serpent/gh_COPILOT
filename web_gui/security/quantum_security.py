"""Quantum-inspired security helpers."""

from __future__ import annotations

from flask import Flask

from web_gui.certificates import quantum_crypto


def init_app(app: Flask) -> None:
    """Provide defaults for quantum security features."""
    app.config.setdefault("QUANTUM_TOKEN_LENGTH", 32)


def generate_token(length: int) -> str:
    """Return a random hexadecimal token generated using quantum-safe methods."""
    return quantum_crypto.generate_quantum_safe_key(length).hex()


__all__ = ["init_app", "generate_token"]
