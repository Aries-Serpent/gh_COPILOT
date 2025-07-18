#!/usr/bin/env python3
import logging

from scripts.automation.quantum_integration_orchestrator import integrate_qubo_problems

logging.getLogger().setLevel(logging.CRITICAL)


def test_integrate_qubo_problems():
    qubos = [
        [[1.0, -2.0], [-2.0, 1.0]],
        [[2.0, -1.0], [-1.0, 2.0]],
    ]
    solution, energy = integrate_qubo_problems(qubos)
    assert solution == [1, 1]
    assert energy == -2.0
