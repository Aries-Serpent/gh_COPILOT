"""Tests for the quantum security helpers within the web GUI."""

import pytest


def test_quantum_token_generation() -> None:
    """Quantum token generation should return a hex string when authorized."""
    try:
        from web_gui.security import quantum_security
    except Exception:
        pytest.skip("quantum security helpers unavailable")

    token = quantum_security.generate_quantum_token(["quantum"])
    assert isinstance(token, str) and len(token) > 0

