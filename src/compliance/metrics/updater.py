"""Utilities for computing compliance metric aggregates."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Mapping


@dataclass
class MetricsUpdater:
    """Combine raw metric scores into a single composite value.

    The updater applies a weighted average to individual metric scores and
    rounds the result to the desired precision.  Weights are normalised so that
    the final score is always in the range ``[0.0, 1.0]`` regardless of the
    provided weight magnitudes.
    """

    weights: Mapping[str, float] = field(
        default_factory=lambda: {"lint": 0.4, "tests": 0.4, "placeholders": 0.2}
    )
    precision: int = 2

    def composite(self, scores: Mapping[str, float]) -> float:
        """Return the normalised weighted score for ``scores``.

        Missing metrics simply contribute ``0``.  The result is rounded to the
        number of decimal places specified by ``precision``.  A ``0`` score is
        returned when the total weight is ``0`` to avoid division errors.
        """

        total_weight = sum(self.weights.values())
        if total_weight <= 0:
            return 0.0

        total = Decimal("0")
        for key, weight in self.weights.items():
            total += Decimal(str(scores.get(key, 0.0))) * Decimal(str(weight))

        result = total / Decimal(str(total_weight))
        quant = Decimal("1").scaleb(-self.precision)
        return float(result.quantize(quant, rounding=ROUND_HALF_UP))
