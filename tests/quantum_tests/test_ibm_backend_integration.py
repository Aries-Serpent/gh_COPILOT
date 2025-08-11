import pytest

import importlib.util
from pathlib import Path


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
    """Verify real provider initialization when token is available."""
    monkeypatch.delenv("IBM_BACKEND", raising=False)
    ibm_backend = _load_ibm_backend()
    backend, use_hw = ibm_backend.init_ibm_backend()
    assert backend is not None
    assert use_hw is True
