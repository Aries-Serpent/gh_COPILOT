from ghc_quantum.framework import SimulatorBackend, QuantumExecutor, run_with_fallback
from ghc_quantum.models import ParityModel


def test_run_with_fallback_handles_failure():
    def build():
        raise RuntimeError

    def classical():
        return "classic"

    result = run_with_fallback(build, classical, executor=QuantumExecutor(SimulatorBackend()))
    assert result == "classic"


def test_parity_model_classical_fallback(monkeypatch):
    model = ParityModel([1, 0, 1])

    def fail(*_, **__):  # pragma: no cover - test helper
        raise RuntimeError

    monkeypatch.setattr(model.executor, "run", fail)
    assert model.run() == 0  # 1+0+1 is even
