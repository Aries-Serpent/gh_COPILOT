"""Prototype Variational Quantum Eigensolver demo with simulator fallback."""

from __future__ import annotations

from ghc_quantum.utils.backend_provider import get_backend

try:  # pragma: no cover - optional dependency
    from qiskit.circuit import QuantumCircuit
    from qiskit.primitives import BackendEstimator, Estimator
    from qiskit.quantum_info import SparsePauliOp
    from scipy.optimize import minimize
except Exception:  # pragma: no cover - qiskit may be missing
    QuantumCircuit = BackendEstimator = Estimator = SparsePauliOp = minimize = None


def run_vqe_demo(use_hardware: bool = False) -> float | None:
    """Estimate ground state energy of a single-qubit ``Z`` operator."""

    if QuantumCircuit is None:
        return None

    backend = get_backend(use_hardware=True) if use_hardware else None
    hamiltonian = SparsePauliOp.from_list([("Z", 1.0)])

    def energy(theta):
        circuit = QuantumCircuit(1)
        circuit.ry(theta[0], 0)
        if backend is not None and BackendEstimator is not None:
            estimator = BackendEstimator(backend=backend, options={"shots": 1024})
        else:
            estimator = Estimator()
        return estimator.run(circuit, hamiltonian).result().values[0]

    result = minimize(lambda x: energy(x), x0=[0.0], method="COBYLA")
    return float(result.fun)


__all__ = ["run_vqe_demo"]

