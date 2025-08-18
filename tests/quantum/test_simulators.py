import time
from collections.abc import Sequence

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


def test_simple_simulator_echoes_circuit():
    sim = SimpleSimulator()
    result = sim.run("H", shots=1, seed=123, extra="ignored")
    assert result == {"simulated": True, "circuit": "H"}


def test_simple_simulator_failure_bad_str():
    sim = SimpleSimulator()
    with pytest.raises(ValueError):
        sim.run(BadStr())
