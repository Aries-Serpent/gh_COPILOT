from src.quantum.simulators import BasicSimulator, SimpleSimulator, QuantumSimulator


def test_basic_simulator_all_zero_output():
    sim = BasicSimulator(shots=10)
    result = sim.run(["q0", "q1"], extra="ignore")
    assert result == {"00": 10}


def test_simulators_share_interface():
    for cls in (BasicSimulator, SimpleSimulator):
        assert issubclass(cls, QuantumSimulator)
