#!/usr/bin/env python3
from quantum_algorithm_library_expansion import (
    EnterpriseUtility,
    demo_grover_search,
    demo_quantum_teleportation,
    demo_quantum_fourier_transform,
)
import logging


def test_perform_utility_function_runs():
    util = EnterpriseUtility()
    assert util.perform_utility_function() is True


def test_demo_grover_search_returns_int():
    result = demo_grover_search()
    assert isinstance(result, int)


def test_demo_quantum_teleportation():
    dm = demo_quantum_teleportation()
    assert len(dm) == 2 and len(dm[0]) == 2


def test_demo_quantum_fourier_transform():
    vec = demo_quantum_fourier_transform()
    assert len(vec) == 4
