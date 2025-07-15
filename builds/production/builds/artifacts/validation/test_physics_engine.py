#!/usr/bin/env python3
from physics_optimization_engine import PhysicsOptimizationEngine
import logging


def test_grover_search_found():
    engine = PhysicsOptimizationEngine()
    data = [1, 2, 3, 4]
    assert engine.grover_search(data, 3) == 2


def test_shor_factorization():
    engine = PhysicsOptimizationEngine()
    assert set(engine.shor_factorization(15)) == {3, 5}


def test_fourier_transform():
    engine = PhysicsOptimizationEngine()
    result = engine.fourier_transform([0, 1, 0, -1])
    assert len(result) == 4
