"""Simple cost model for quantum executions.

The real project would integrate provider specific pricing.  For the unit
tests we provide a deterministic and lightweight estimator that derives costs
from the circuit description length.  This keeps the interface stable while
remaining fully offline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class CostEstimate:
    """Represents an execution cost estimate."""

    estimated_time: float
    estimated_credits: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "estimated_time": self.estimated_time,
            "estimated_credits": self.estimated_credits,
        }


def estimate_cost(circuit: Any, shots: int = 1024) -> Dict[str, float]:
    """Estimate execution cost for ``circuit``.

    Parameters
    ----------
    circuit:
        Circuit object or description.  Only its string representation length is
        used which keeps the estimator deterministic and dependency free.
    shots:
        Number of repetitions.  Increasing shots linearly increases the
        estimates.
    """

    complexity = len(str(circuit)) or 1
    time = 0.001 * shots * complexity
    credits = 0.01 * shots * complexity
    return CostEstimate(time, credits).to_dict()


__all__ = ["estimate_cost", "CostEstimate"]

