import numpy as np
import pytest
from unittest.mock import patch

from ghc_quantum.optimizers.quantum_optimizer import QuantumOptimizer

pytestmark = pytest.mark.timeout(60)


def test_simulated_annealing_runs():
    def obj(x):
        return np.sum((x - 1) ** 2)

    optimizer = QuantumOptimizer(obj, [(-2, 2), (-2, 2)], method="simulated_annealing")
    result = optimizer.run(x0=np.array([0.0, 0.0]), max_iter=10)
    assert "best_result" in result["result"]
    assert isinstance(result["result"]["best_value"], float)


def test_set_backend_fallback(monkeypatch):
    monkeypatch.setattr(
        "ghc_quantum.optimizers.quantum_optimizer.init_ibm_backend",
        lambda **_: (object(), False),
        raising=False,
    )
    opt = QuantumOptimizer(lambda x: 0, [(0, 1)])
    opt.set_backend(None, use_hardware=True)
    assert opt.use_hardware is False


@pytest.mark.hardware
def test_set_backend_hardware(monkeypatch):
    backend = object()
    monkeypatch.setattr(
        "ghc_quantum.optimizers.quantum_optimizer.init_ibm_backend",
        lambda **_: (backend, True),
    )
    opt = QuantumOptimizer(lambda x: 0, [(0, 1)], use_hardware=True)
    opt.set_backend(None, use_hardware=True)
    assert opt.use_hardware is True
    assert opt.backend is backend


def test_qaoa_runs_with_progress():
    pytest.importorskip("qiskit_algorithms")
    def obj(x):
        return float(np.sum(x))

    optimizer = QuantumOptimizer(obj, [(0, 1)], method="qaoa")
    summary = optimizer.run(n_qubits=1, reps=1, max_iter=2)
    events = [e["event"] for e in summary["history"]]
    assert "qaoa_complete" in events
    assert any(e == "qaoa_progress" for e in events)


def test_vqe_runs_with_progress():
    pytest.importorskip("qiskit_algorithms")
    def obj(x):
        return float(np.sum(x))

    optimizer = QuantumOptimizer(obj, [(0, 1)], method="vqe")
    summary = optimizer.run(n_qubits=1, reps=1, max_iter=2)
    events = [e["event"] for e in summary["history"]]
    assert "vqe_complete" in events
    assert any(e == "vqe_progress" for e in events)


def test_simulated_annealing_uses_progress_bar():
    def obj(x):
        return np.sum((x - 1) ** 2)

    optimizer = QuantumOptimizer(obj, [(-2, 2), (-2, 2)], method="simulated_annealing")
    with patch("ghc_quantum.optimizers.quantum_optimizer.tqdm") as mock_tqdm:
        mock_tqdm.side_effect = lambda *args, **kwargs: args[0]
        optimizer.run(x0=np.array([0.0, 0.0]), max_iter=5)
        assert mock_tqdm.called
        assert "[PROGRESS]" in mock_tqdm.call_args.kwargs.get("desc", "")


def test_basin_hopping_fallback_uses_progress_bar():
    def obj(x):
        return float(np.sum(x ** 2))

    optimizer = QuantumOptimizer(obj, [(-1, 1)], method="basin_hopping")

    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("scipy"):
            raise ImportError
        return real_import(name, *args, **kwargs)

    with patch("ghc_quantum.optimizers.quantum_optimizer.tqdm") as mock_tqdm, patch(
        "builtins.__import__", side_effect=fake_import
    ):
        mock_tqdm.side_effect = lambda *args, **kwargs: args[0]
        optimizer.run(niter=5)
        assert mock_tqdm.called
        assert "[PROGRESS]" in mock_tqdm.call_args.kwargs.get("desc", "")
