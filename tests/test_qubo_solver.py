import logging

from advanced_qubo_optimization import solve_qubo_bruteforce

logging.getLogger().setLevel(logging.CRITICAL)


def test_solve_qubo_bruteforce():
    matrix = [[1.0, -2.0], [-2.0, 1.0]]
    solution, energy = solve_qubo_bruteforce(matrix)
    assert solution == [1, 1]
    assert energy == -2.0
