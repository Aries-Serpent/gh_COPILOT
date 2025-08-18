"""Minimal state-vector simulator for quantum circuits."""
from __future__ import annotations

from typing import Iterable, Tuple

import numpy as np

from . import gate_ops

Operation = Tuple[str, Tuple[int, ...]]


def run_circuit(num_qubits: int, ops: Iterable[Operation]) -> np.ndarray:
    """Execute ``ops`` on ``num_qubits`` initialized to ``|0...0>``."""
    state = np.zeros(2**num_qubits, dtype=complex)
    state[0] = 1.0

    for name, qubits in ops:
        if name in gate_ops.GATE_MAP:
            gate = gate_ops.GATE_MAP[name]
            state = gate_ops.apply_single_qubit_gate(state, gate, qubits[0], num_qubits)
        elif name == "CNOT":
            state = gate_ops.apply_cnot(state, qubits[0], qubits[1], num_qubits)
        else:
            raise ValueError(f"unknown gate {name}")
    return state


if __name__ == "__main__":  # pragma: no cover - manual profiling entry
    circuit = [("H", (0,)), ("CNOT", (0, 1))]
    run_circuit(2, circuit)
