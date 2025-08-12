"""Unit tests for the :mod:`quantum_enhanced_framework` module."""

from web_gui.scripts.flask_apps.quantum_enhanced_framework import (
    QuantumEnhancedFramework,
)


def test_execute_with_fallback_uses_quantum_when_enabled() -> None:
    """Quantum function should run when quantum mode is enabled."""

    framework = QuantumEnhancedFramework()
    framework.quantum_enabled = True

    def quantum() -> str:
        return "quantum"

    result = framework.execute_with_fallback(lambda: "classical", quantum)
    assert result == "quantum"


def test_execute_with_fallback_uses_classical_when_disabled() -> None:
    """Falls back to classical function when quantum is disabled."""

    framework = QuantumEnhancedFramework()
    framework.quantum_enabled = False

    result = framework.execute_with_fallback(lambda: "classical", lambda: "quantum")
    assert result == "classical"


def test_execute_with_fallback_handles_quantum_errors() -> None:
    """Errors from ghc_quantum path should trigger classical fallback."""

    framework = QuantumEnhancedFramework()
    framework.quantum_enabled = True

    def quantum() -> str:
        raise RuntimeError("boom")

    result = framework.execute_with_fallback(lambda: "classical", quantum)
    assert result == "classical"

