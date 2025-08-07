"""Basic pattern recognition utilities."""

from __future__ import annotations

from typing import Iterable, List

__all__ = ["find_repeated"]


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
