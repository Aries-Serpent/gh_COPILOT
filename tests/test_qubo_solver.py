import numpy as np

from quantum import solve_qubo_brute_force


def test_brute_force_qubo_solver():
    Q = np.array([[1, -1], [-1, 2]], dtype=float)
    sol, energy = solve_qubo_brute_force(Q)
    assert energy == 0
    assert sol.tolist() == [0, 0]
