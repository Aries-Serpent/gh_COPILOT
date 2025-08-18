import numpy as np
import pytest
from hypothesis import given, strategies as st

import quantum.gate_ops as gate_ops
import quantum.sim_runner as sim_runner


def basis_state(index: int, num_qubits: int) -> np.ndarray:
    state = np.zeros(2**num_qubits, dtype=complex)
    state[index] = 1.0
    return state


def test_single_qubit_gates():
    num_qubits = 1
    state = basis_state(0, num_qubits)
    for gate in [
        gate_ops.X,
        gate_ops.Y,
        gate_ops.Z,
        gate_ops.H,
        gate_ops.S,
        gate_ops.T,
        gate_ops.IDENTITY,
    ]:
        new_state = gate_ops.apply_single_qubit_gate(state, gate, 0, num_qubits)
        assert new_state.shape == state.shape


def test_apply_cnot_and_error():
    num_qubits = 2
    state = basis_state(1, num_qubits)  # |01>
    new_state = gate_ops.apply_cnot(state, 1, 0, num_qubits)
    assert np.allclose(new_state, basis_state(3, num_qubits))
    with pytest.raises(ValueError):
        gate_ops.apply_cnot(state, 0, 0, num_qubits)
    with pytest.raises(ValueError):
        gate_ops.apply_cnot(state, 2, 0, num_qubits)


@given(bit=st.integers(0, 1))
def test_hadamard_superposition(bit):
    state = basis_state(bit, 1)
    result = gate_ops.apply_single_qubit_gate(state, gate_ops.H, 0, 1)
    assert np.isclose(np.linalg.norm(result), 1.0)


@given(st.sampled_from([(0, 1), (1, 0)]))
def test_entanglement(control_target):
    ct, tt = control_target
    state = sim_runner.run_circuit(2, [("H", (ct,)), ("CNOT", (ct, tt))])
    probs = np.abs(state) ** 2
    assert np.isclose(probs[0], 0.5)
    assert np.isclose(probs[3], 0.5)
    assert np.isclose(probs[1], 0.0)
    assert np.isclose(probs[2], 0.0)


def test_run_circuit_unknown_gate():
    with pytest.raises(ValueError):
        sim_runner.run_circuit(1, [("UNKNOWN", (0,))])


def test_single_qubit_gate_invalid_qubit():
    with pytest.raises(ValueError):
        gate_ops.single_qubit_gate_matrix(gate_ops.X, 1, 1)
