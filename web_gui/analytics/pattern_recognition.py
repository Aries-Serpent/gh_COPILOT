"""Pattern recognition utilities for the web GUI."""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

from web_gui.monitoring.performance_metrics import collect_performance_metrics

__all__ = ["find_repeated", "PatternRecognizer"]


def find_repeated(values: Iterable[int]) -> List[int]:
    """Return sorted values that appear more than once in ``values``."""
    seen: set[int] = set()
    repeated: set[int] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        else:
            seen.add(value)
    return sorted(repeated)


class PatternRecognizer:
    """Stub recognizer using current performance metrics as features."""

    def current_metrics(self) -> Dict[str, float]:
        """Expose current performance metrics for downstream analysis."""
        return collect_performance_metrics()

    def detect(self, values: Sequence[int]) -> List[int]:
        """Identify repeated values using :func:`find_repeated`."""
        return find_repeated(values)
