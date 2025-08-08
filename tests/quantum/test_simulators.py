from src.quantum.simulators import BasicSimulator, QuantumSimulator, SimpleSimulator


def test_simple_simulator_runs_without_hardware():
    sim = SimpleSimulator()
    circuit = "dummy-circuit"
    assert sim.run(circuit) == {"simulated": True, "circuit": "dummy-circuit"}


def test_simple_simulator_is_interface():
    assert issubclass(SimpleSimulator, QuantumSimulator)


def test_basic_simulator_shots_override():
    sim = BasicSimulator()
    assert sim.run(["q0"], shots=3) == {"0": 3}
