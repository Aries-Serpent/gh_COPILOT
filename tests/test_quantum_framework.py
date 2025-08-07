from web_gui.scripts.flask_apps.quantum_enhanced_framework import (
    QuantumEnhancedFramework,
)


def test_quantum_framework_fallback() -> None:
    """Running an unknown algorithm returns a fallback message."""
    framework = QuantumEnhancedFramework()
    result = framework.run_algorithm("noop")
    assert isinstance(result, dict)

