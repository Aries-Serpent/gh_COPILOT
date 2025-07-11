"""Simple brute-force QUBO solver."""
from itertools import product
from typing import Tuple

import numpy as np


def solve_qubo_brute_force(Q: np.ndarray) -> Tuple[np.ndarray, float]:
    """Return binary vector ``x`` minimizing ``x^T Q x``.

    This method enumerates all ``2^n`` binary vectors for an ``n``-variable
    problem. It therefore has exponential time complexity and is intended only
    for very small matrices.

    Parameters
    ----------
    Q : numpy.ndarray
        Square QUBO matrix. ``Q`` must be a two-dimensional square array.

    Returns
    -------
    Tuple[numpy.ndarray, float]
        Tuple ``(x, energy)`` where ``x`` is the optimal binary vector and
        ``energy`` is the minimum value of ``x^T Q x``.

    Raises
    ------
    ValueError
        If ``Q`` is not a two-dimensional square array.
    """

    if Q.ndim != 2 or Q.shape[0] != Q.shape[1]:
        raise ValueError("Q must be a square 2D numpy array")

    n = Q.shape[0]
    best_energy = float("inf")
    best_solution = None
    for bits in product([0, 1], repeat=n):
        x = np.array(bits, dtype=int)
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
