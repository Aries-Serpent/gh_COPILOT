from src.quantum.simulators import QuantumSimulator, SimpleSimulator


def test_simple_simulator_runs_without_hardware():
    sim = SimpleSimulator()
    circuit = "dummy-circuit"
    assert sim.run(circuit) == {"simulated": True, "circuit": "dummy-circuit"}


def test_simple_simulator_is_interface():
    assert issubclass(SimpleSimulator, QuantumSimulator)
