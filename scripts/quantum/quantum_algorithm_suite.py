"""Quantum algorithm suite placeholder."""
from __future__ import annotations

import logging

__all__ = ["QuantumAlgorithmSuite"]


class QuantumAlgorithmSuite:
    """Placeholder quantum algorithms."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def grover(self) -> str:
        self.logger.info("Running Grover placeholder")
        return "grover"

    def shor(self) -> str:
        self.logger.info("Running Shor placeholder")
        return "shor"
