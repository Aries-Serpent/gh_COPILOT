"""Stub model and interface for pattern recognition."""

from __future__ import annotations

from typing import Iterable, List


class StubModel:
    """Placeholder model returning inputs."""

    def predict(self, data: Iterable[str]) -> List[str]:
        return list(data)


class PatternRecognizer:
    """Interface for future ML-based pattern recognition."""

    def __init__(self, model: StubModel | None = None) -> None:
        self.model = model or StubModel()

    def recognize(self, data: Iterable[str]) -> List[str]:
        """Return recognized patterns from ``data``."""
        return self.model.predict(data)
