"""Example model demonstrating quantum execution with classical fallback."""

from __future__ import annotations

from typing import Any, Sequence

from .base import QuantumModel


class ParityModel(QuantumModel):
    """Compute the parity of ``data`` using a quantum circuit when possible.

    The model builds a trivial circuit representation and relies on
    :class:`quantum.framework.QuantumExecutor` for execution. If quantum
    execution fails, the parity is computed classically.
    """

    def __init__(self, data: Sequence[int], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.data = list(data)

    def build_circuit(self) -> str:
        return f"parity:{self.data}"

    # Classical fallback -------------------------------------------------
    def _classical_parity(self) -> int:
        return sum(self.data) % 2

    def run(self, **kwargs: Any) -> Any:  # type: ignore[override]
        try:
            return super().run(**kwargs)
        except Exception:
            return self._classical_parity()


__all__ = ["ParityModel"]

