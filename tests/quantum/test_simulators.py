import time
from collections.abc import Sequence

import numpy as np
import pytest

from src.quantum.simulators.base import QuantumSimulator
from src.quantum.simulators.basic import BasicSimulator
from src.quantum.simulators.simple import SimpleSimulator


class BadCircuit(Sequence):
    def __len__(self) -> int:
        return 1

    def __getitem__(self, index: int):
        raise ValueError("bad circuit")


class BadStr:
    def __str__(self) -> str:  # pragma: no cover - called only on failure
        raise ValueError("no string")


def test_abstract_simulator_instantiation_fails():
    with pytest.raises(TypeError):
        QuantumSimulator()  # type: ignore[abstract]


def test_basic_simulator_runs_and_overrides_shots():
    sim = BasicSimulator(shots=5)
    result = sim.run([0, 1])
    assert result == {"00": 5}

    result = sim.run([0, 1], shots=3)
    assert result == {"00": 3}


def test_basic_simulator_classical_fallback():
    sim = BasicSimulator()
    result = sim.run(0)
    assert result == {"0": sim.shots}


def test_basic_simulator_failure_bad_circuit():
    sim = BasicSimulator()
    with pytest.raises(ValueError):
        sim.run(BadCircuit())


def test_basic_simulator_caching_improves_runtime():
    sim = BasicSimulator()
    circuit = list(range(10000))
    start = time.perf_counter()
    sim.run(circuit)
    first = time.perf_counter() - start
    start = time.perf_counter()
    sim.run(circuit)
    second = time.perf_counter() - start
    assert second <= first


def classical_basic(circuit, shots):
    zeros = "0" * (len(list(circuit)) if isinstance(circuit, Sequence) else 1)
    return {zeros: shots}


def test_basic_simulator_beats_classical():
    sim = BasicSimulator()
    circuit = list(range(10000))
    # warm cache and baseline
    classical_basic(circuit, sim.shots)
    sim.run(circuit)

    start = time.perf_counter()
    classical_basic(circuit, sim.shots)
    classical_time = time.perf_counter() - start

    start = time.perf_counter()
    sim.run(circuit)
    quantum_time = time.perf_counter() - start

    assert quantum_time <= classical_time


def test_simple_simulator_echoes_circuit():
    sim = SimpleSimulator()
    result = sim.run("H", shots=1, seed=123, extra="ignored")
    assert result == {"simulated": True, "circuit": "H"}


def test_simple_simulator_classical_fallback():
    sim = SimpleSimulator()
    result = sim.run(42)
    assert result == {"simulated": True, "circuit": "42"}


def test_simple_simulator_failure_bad_str():
    sim = SimpleSimulator()
    with pytest.raises(ValueError):
        sim.run(BadStr())


def classical_mm(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def test_matrix_dot_matches_numpy_and_beats_classical():
    a = np.arange(9.0).reshape(3, 3)
    b = np.arange(9.0, 18.0).reshape(3, 3)
    expected = a @ b

    start = time.perf_counter()
    res = QuantumSimulator.dot(a, b)
    first = time.perf_counter() - start
    assert np.allclose(res, expected)

    start = time.perf_counter()
    QuantumSimulator.dot(a, b)
    second = time.perf_counter() - start
    assert second <= first

    start = time.perf_counter()
    classical_mm(a.tolist(), b.tolist())
    classical_time = time.perf_counter() - start
    assert second <= classical_time

    with pytest.raises(ValueError):
        QuantumSimulator.dot(a[:, :2], b)
