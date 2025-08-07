from web_gui.scripts.flask_apps.quantum_enhanced_framework import (
    QuantumEnhancedFramework,
)


def test_quantum_framework_fallback() -> None:
    """Running an unknown algorithm returns a fallback message."""
    framework = QuantumEnhancedFramework()
    result = framework.run_algorithm("noop")
    assert isinstance(result, dict)


def test_execute_with_fallback_uses_classical() -> None:
    """execute_with_fallback should call the classical function."""
    framework = QuantumEnhancedFramework()
    result = framework.execute_with_fallback(lambda: "classic")
    assert result == "classic"


def test_quantum_enabled_flag_is_boolean() -> None:
    """quantum_enabled attribute should always be a boolean."""
    framework = QuantumEnhancedFramework()
    assert isinstance(framework.quantum_enabled, bool)

