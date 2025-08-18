import numpy as np

IDENTITY = np.array([[1, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
S = np.array([[1, 0], [0, 1j]], dtype=complex)
T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)

CNOT = np.array(
    [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
    ],
    dtype=complex,
)

GATE_MAP = {"I": IDENTITY, "X": X, "Y": Y, "Z": Z, "H": H, "S": S, "T": T}


def single_qubit_gate_matrix(gate: np.ndarray, qubit: int, num_qubits: int) -> np.ndarray:
    """Return the full operator for ``gate`` acting on ``qubit``."""
    if gate.shape != (2, 2):  # pragma: no cover - defensive programming
        raise ValueError("gate must be 2x2")
    if not 0 <= qubit < num_qubits:
        raise ValueError("invalid qubit index")

    op = 1
    for i in range(num_qubits):
        op = np.kron(op, gate if i == qubit else IDENTITY)
    return op


def apply_single_qubit_gate(
    state: np.ndarray, gate: np.ndarray, qubit: int, num_qubits: int
) -> np.ndarray:
    """Apply a single-qubit ``gate`` to ``state``."""
    full_gate = single_qubit_gate_matrix(gate, qubit, num_qubits)
    return full_gate @ state


def apply_cnot(
    state: np.ndarray, control: int, target: int, num_qubits: int
) -> np.ndarray:
    """Apply a controlled NOT gate to ``state``."""
    if control == target:
        raise ValueError("control and target must differ")
    if not (0 <= control < num_qubits and 0 <= target < num_qubits):
        raise ValueError("invalid qubit index")

    size = 2**num_qubits
    new_state = np.zeros_like(state)
    for i in range(size):
        bits = [(i >> (num_qubits - 1 - k)) & 1 for k in range(num_qubits)]
        if bits[control] == 1:
            bits[target] ^= 1
        j = 0
        for bit in bits:
            j = (j << 1) | bit
        new_state[j] = state[i]
    return new_state
