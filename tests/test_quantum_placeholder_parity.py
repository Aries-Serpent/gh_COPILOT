"""Simulator parity tests for quantum placeholder modules."""

import importlib
import importlib.util
import types
from pathlib import Path
import sys


def _load(name: str):
    path = Path(__file__).resolve().parents[1] / "scripts" / "quantum_placeholders" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


REPO_ROOT = Path(__file__).resolve().parents[1]
quantum_pkg = types.ModuleType("quantum")
quantum_pkg.__path__ = [str(REPO_ROOT / "quantum")]
sys.modules.setdefault("quantum", quantum_pkg)
utils_pkg = types.ModuleType("quantum.utils")
utils_pkg.__path__ = [str(REPO_ROOT / "quantum" / "utils")]
sys.modules.setdefault("quantum.utils", utils_pkg)
backend_stub = types.ModuleType("quantum.utils.backend_provider")
backend_stub.get_backend = lambda *_, **__: None
sys.modules.setdefault("quantum.utils.backend_provider", backend_stub)
audit_stub = types.ModuleType("quantum.utils.audit_log")
audit_stub.log_quantum_audit = lambda *_, **__: None
sys.modules.setdefault("quantum.utils.audit_log", audit_stub)

scripts_pkg = types.ModuleType("scripts")
scripts_pkg.__path__ = [str(REPO_ROOT / "scripts")]
sys.modules.setdefault("scripts", scripts_pkg)

init_spec = importlib.util.spec_from_file_location(
    "scripts.quantum_placeholders", REPO_ROOT / "scripts" / "quantum_placeholders" / "__init__.py"
)
qp_pkg = importlib.util.module_from_spec(init_spec)
sys.modules["scripts.quantum_placeholders"] = qp_pkg
assert init_spec.loader is not None
init_spec.loader.exec_module(qp_pkg)


def _load(name: str):
    module_name = f"scripts.quantum_placeholders.{name}"
    path = REPO_ROOT / "scripts" / "quantum_placeholders" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


quantum_annealing = _load("quantum_annealing")
quantum_entanglement_correction = _load("quantum_entanglement_correction")
quantum_placeholder_algorithm = _load("quantum_placeholder_algorithm")
quantum_superposition_search = _load("quantum_superposition_search")


def test_quantum_annealing_parity(monkeypatch):
    monkeypatch.setattr(quantum_annealing, "QISKIT_AVAILABLE", False, raising=False)
    vec = [1.0, -1.0]
    sim = quantum_annealing.run_quantum_annealing(vec)
    hw = quantum_annealing.run_quantum_annealing(vec, use_hardware=True)
    assert sim == hw


def test_quantum_superposition_parity(monkeypatch):
    monkeypatch.setattr(quantum_superposition_search, "QISKIT_AVAILABLE", False, raising=False)
    sim = quantum_superposition_search.run_quantum_superposition_search(2)
    hw = quantum_superposition_search.run_quantum_superposition_search(2, use_hardware=True)
    assert sim == hw


def test_entanglement_correction_parity(monkeypatch):
    monkeypatch.setattr(quantum_entanglement_correction, "QISKIT_AVAILABLE", False, raising=False)
    sim = quantum_entanglement_correction.run_entanglement_correction()
    hw = quantum_entanglement_correction.run_entanglement_correction(use_hardware=True)
    assert sim == hw


def test_placeholder_algorithm_identity():
    data = [1, 2, 3]
    assert quantum_placeholder_algorithm.simulate_quantum_process(data) == data
