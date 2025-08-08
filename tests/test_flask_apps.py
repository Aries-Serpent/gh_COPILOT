from importlib import import_module
import pytest
from web_gui.scripts.flask_apps.quantum_enhanced_framework import (
    QuantumEnhancedFramework,
    quantum_bp,
)


@pytest.mark.parametrize(
    "name",
    [
        "web_gui.scripts.flask_apps.quantum_enhanced_framework",
        "web_gui.scripts.flask_apps.enterprise_dashboard",
    ],
)
def test_flask_app_modules_import(name: str) -> None:
    """Flask app modules should import; skip if environment guards trigger."""
    try:
        module = import_module(name)
    except RuntimeError as exc:  # pragma: no cover - environment guard
        pytest.skip(str(exc))
    else:
        assert module is not None


def test_framework_available_algorithms() -> None:
    """QuantumEnhancedFramework should list available algorithms."""
    framework = QuantumEnhancedFramework()
    assert isinstance(framework.available_algorithms(), list)


def test_quantum_blueprint_registered() -> None:
    """Blueprint should expose the expected name."""
    assert quantum_bp.name == "quantum"

