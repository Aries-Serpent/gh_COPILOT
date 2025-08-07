"""Pattern recognition utilities."""

from __future__ import annotations

from collections import Counter
from typing import Any, Sequence, Dict

__all__ = ["detect_patterns"]


def detect_patterns(items: Sequence[Any]) -> Dict[Any, int]:
    """Return frequency counts for ``items``."""
    return dict(Counter(items))
