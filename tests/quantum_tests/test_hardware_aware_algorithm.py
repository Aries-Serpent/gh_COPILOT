import pytest

from ghc_quantum.algorithms import hardware_aware
from ghc_quantum.utils import backend_provider


@pytest.mark.skipif(backend_provider.Aer is None, reason="Qiskit not available")
def test_hardware_aware_algorithm_respects_flag(monkeypatch):
    called = {}

    def fake_backend(use_hardware=None):
        called["flag"] = use_hardware

        class DummyBackend:
            pass

        return DummyBackend()

    def fake_execute(qc, backend, shots):
        class DummyJob:
            def result(self):
                return None

        return DummyJob()

    monkeypatch.setattr(hardware_aware, "get_backend", fake_backend)
    monkeypatch.setattr(hardware_aware, "execute", fake_execute)

    algo = hardware_aware.HardwareAwareAlgorithm(use_hardware=True)
    assert algo.execute_algorithm()
    assert called["flag"] is True

