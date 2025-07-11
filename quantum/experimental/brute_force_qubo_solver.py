"""Simple brute-force QUBO solver."""
from itertools import product
from typing import Tuple

import numpy as np


def solve_qubo_brute_force(Q: np.ndarray) -> Tuple[np.ndarray, float]:
    """Return binary vector x that minimizes x^T Q x."""
    n = Q.shape[0]
    best_energy = float("inf")
    best_solution = None
    for bits in product([0, 1], repeat=n):
        x = np.array(bits)
        energy = float(x @ Q @ x)
        if energy < best_energy:
            best_energy = energy
            best_solution = x
    return best_solution, best_energy


if __name__ == "__main__":
    # Example usage
    Q = np.array([[1, -1], [-1, 2]], dtype=float)
    sol, energy = solve_qubo_brute_force(Q)
    print("Solution:", sol)
    print("Energy:", energy)
