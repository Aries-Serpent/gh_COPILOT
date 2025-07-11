from physics_optimization_engine import PhysicsOptimizationEngine
import numpy as np


def test_grover_search_found():
    engine = PhysicsOptimizationEngine()
    data = [1, 2, 3, 4]
    assert engine.grover_search(data, 3) == 2


def test_shor_factorization():
    engine = PhysicsOptimizationEngine()
    assert set(engine.shor_factorization(15)) == {3, 5}


def test_fourier_transform():
    engine = PhysicsOptimizationEngine()
    data = [0, 1, 0, -1]
    result = engine.fourier_transform(data)
    expected = np.fft.fft(data) / np.sqrt(len(data))
    assert np.allclose(result, expected, atol=1e-6)
