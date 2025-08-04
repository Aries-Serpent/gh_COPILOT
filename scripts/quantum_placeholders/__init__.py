"""Placeholder modules for future quantum features.

These modules are stubs referencing planned quantum capabilities
outlined in the whitepaper. They are excluded from production paths
and serve only as importable placeholders for future work.
"""

from __future__ import annotations

import os

PLACEHOLDER_ONLY = True


def ensure_not_production() -> None:
    """Raise an error if placeholders load in production."""
    if os.environ.get("GH_COPILOT_ENV") == "production":
        msg = "Quantum placeholder modules should not be used in production."
        raise RuntimeError(msg)


from . import (
    quantum_placeholder_algorithm,
    quantum_annealing,
    quantum_superposition_search,
    quantum_entanglement_correction,
)

__all__ = [
    "quantum_placeholder_algorithm",
    "quantum_annealing",
    "quantum_superposition_search",
    "quantum_entanglement_correction",
]
