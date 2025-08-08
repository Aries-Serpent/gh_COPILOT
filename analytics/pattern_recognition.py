"""Basic pattern recognition utilities."""

from __future__ import annotations

from typing import Iterable, List, Dict

__all__ = ["find_repeated", "detect_patterns"]


def find_repeated(values: Iterable[int]) -> List[int]:
    """Return sorted values that appear more than once in ``values``."""
    seen = set()
    repeated = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        else:
            seen.add(value)
    return sorted(repeated)


def detect_patterns(values: Iterable[int]) -> Dict[int, int]:
    """Return a frequency map for ``values``."""

    counts: Dict[int, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
