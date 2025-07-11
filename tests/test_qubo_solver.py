import numpy as np
import pytest

from quantum import solve_qubo_brute_force


def test_brute_force_qubo_solver_small():
    Q = np.array([[1, -1], [-1, 2]], dtype=float)
    sol, energy = solve_qubo_brute_force(Q)
    assert energy == 0
    assert sol.tolist() == [0, 0]


def test_brute_force_qubo_solver_larger():
    Q = np.array(
        [[2, -1, 0],
         [-1, 2, -1],
         [0, -1, 2]],
        dtype=float,
    )
    sol, energy = solve_qubo_brute_force(Q)
    assert energy == 0
    assert sol.tolist() == [0, 0, 0]


def test_brute_force_qubo_solver_tie_break():
    Q = np.zeros((2, 2), dtype=float)
    sol, energy = solve_qubo_brute_force(Q)
    assert energy == 0
    assert sol.tolist() == [0, 0]


def test_brute_force_qubo_solver_invalid():
    with pytest.raises(ValueError):
        solve_qubo_brute_force(np.array([[1, 2, 3], [4, 5, 6]]))
