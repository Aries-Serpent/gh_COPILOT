"""Tests for quantum-related security helpers."""

import pytest


def test_quantum_token_role_requirement() -> None:
    """Generating a quantum token requires the appropriate role."""
    try:
        from web_gui.security import quantum_security
    except Exception:
        pytest.skip("quantum security helpers unavailable")

    with pytest.raises(PermissionError):
        quantum_security.generate_quantum_token(["user"])
    assert isinstance(
        quantum_security.generate_quantum_token(["quantum"]),
        str,
    )

