from unittest.mock import MagicMock

from ghc_quantum.ibm_backend import init_ibm_backend


def test_init_backend_success(monkeypatch):
    backend = object()
    provider = MagicMock()
    provider.return_value.get_backend.return_value = backend
    monkeypatch.setenv("QISKIT_IBM_TOKEN", "token")
    monkeypatch.setenv("IBM_BACKEND", "backend")
    monkeypatch.setattr("ghc_quantum.ibm_backend.IBMProvider", provider)
    def _stub_get_backend_backend(name):
        return backend

    monkeypatch.setattr(
        "ghc_quantum.ibm_backend.Aer", MagicMock(get_backend=_stub_get_backend_backend)
    )
    result, use_hw = init_ibm_backend()
    assert result is backend
    assert use_hw is True


def test_init_backend_no_token(monkeypatch):
    simulator = object()
    monkeypatch.delenv("QISKIT_IBM_TOKEN", raising=False)
    def _stub_get_backend_simulator(name):
        return simulator

    monkeypatch.setattr(
        "ghc_quantum.ibm_backend.Aer", MagicMock(get_backend=_stub_get_backend_simulator)
    )
    result, use_hw = init_ibm_backend()
    assert result is simulator
    assert use_hw is False
