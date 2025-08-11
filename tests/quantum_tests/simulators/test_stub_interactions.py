from src.quantum.simulators import BasicSimulator, SimpleSimulator, QuantumSimulator


def test_basic_simulator_all_zero_output():
    sim = BasicSimulator()
    result = sim.run(["q0", "q1"], shots=10, extra="ignore")
    assert result == {"00": 10}


def test_basic_simulator_accepts_seed():
    sim = BasicSimulator(shots=5)
    assert sim.run(["q0"], seed=123) == {"0": 5}


def test_simple_simulator_accepts_kwargs():
    sim = SimpleSimulator()
    out = sim.run("dummy", shots=1, seed=99, extra="x")
    assert out == {"simulated": True, "circuit": "dummy"}


def test_simulators_share_interface():
    for cls in (BasicSimulator, SimpleSimulator):
        assert issubclass(cls, QuantumSimulator)
