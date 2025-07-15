#!/usr/bin/env python3
"""Minimal Shor implementation for tests."""
from __future__ import annotations

import numpy as np
import logging


class Shor:
    """Provide a fallback factorization routine."""

    def __init__(self, quantum_instance: object | None = None) -> None:
        self.quantum_instance = quantum_instance

    def factor(self, n: int):
        for i in range(2, int(np.sqrt(n)) + 1):
            if n % i == 0:
                return type("Res", (), {"factors": [[i, n // i]]})()
        return type("Res", (), {"factors": [[n, 1]]})()
