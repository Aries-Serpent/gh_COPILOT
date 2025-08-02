import os
import pytest

import importlib.util
from pathlib import Path

os.environ["QISKIT_IBM_TOKEN"] = "TOKEN"


def _load_ibm_backend():
    spec = importlib.util.spec_from_file_location(
        "ibm_backend", Path(__file__).resolve().parents[2] / "quantum" / "ibm_backend.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


@pytest.mark.hardware
def test_backend_initializes_with_real_provider(monkeypatch):
    """Verify provider initialization with token using a mock provider."""
    monkeypatch.delenv("IBM_BACKEND", raising=False)
    ibm_backend = _load_ibm_backend()

    class DummyProvider:
        def __init__(self, token: str):
            assert token == "TOKEN"

        def backends(self, simulator: bool = False, operational: bool = True):
            return ["backend"]

    class DummyAer:
        @staticmethod
        def get_backend(name: str):  # pragma: no cover - not used
            return name

    monkeypatch.setattr(ibm_backend, "IBMProvider", DummyProvider)
    monkeypatch.setattr(ibm_backend, "Aer", DummyAer)
    backend, use_hw = ibm_backend.init_ibm_backend(enforce_hardware=True)
    assert backend == "backend"
    assert use_hw is True
