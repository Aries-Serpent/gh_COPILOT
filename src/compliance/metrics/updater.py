"""Utilities for computing compliance metric aggregates."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Mapping
import math


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

        Missing metrics simply contribute ``0``.  Non-numeric or non-finite
        values (``NaN``/``inf``) are treated as ``0`` to prevent ``Decimal``
        errors when computing the total.  The result is rounded to the number
        of decimal places specified by ``precision``.  A ``0`` score is
        returned when the total weight is ``0`` to avoid division errors.
        """

        if self.precision < 0:
            raise ValueError("precision must be non-negative")

        # Ignore non-positive weights so that callers can disable a metric by
        # setting its weight to ``0`` or a negative number.  This mirrors the
        # behaviour of the tests which expect a zero total weight to yield a
        # ``0`` composite score rather than raising an exception.
        total_weight = sum(w for w in self.weights.values() if w > 0)
        if total_weight <= 0:
            return 0.0

        total = Decimal("0")
        for key, weight in self.weights.items():
            if weight <= 0:
                continue
            # Clamp incoming scores to the range [0.0, 1.0] so that accidental
            # over/under flows do not skew the composite metric.  The clamping
            # mirrors how other parts of the system treat compliance metrics
            # and keeps the final value predictable.
            score = scores.get(key, 0.0)
            try:
                value = float(score)
            except (TypeError, ValueError):
                value = 0.0
            if not math.isfinite(value):
                value = 0.0
            clamped = max(0.0, min(1.0, value))
            total += Decimal(str(clamped)) * Decimal(str(weight))

        result = total / Decimal(str(total_weight))
        quant = Decimal("1").scaleb(-self.precision)
        return float(result.quantize(quant, rounding=ROUND_HALF_UP))
