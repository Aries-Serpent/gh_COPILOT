import importlib
import sys
from unittest import mock


def test_import_no_validation(monkeypatch):
    if "quantum.optimizers.quantum_optimizer" in sys.modules:
        del sys.modules["quantum.optimizers.quantum_optimizer"]
    with mock.patch(
        "utils.cross_platform_paths.CrossPlatformPathManager.get_workspace_path",
        side_effect=RuntimeError("called"),
    ):
        module = importlib.import_module("quantum.optimizers.quantum_optimizer")
    assert module is not None
