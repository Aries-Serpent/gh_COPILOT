from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any, Dict, Optional, Tuple

import numpy as np


class QuantumSimulator(ABC):
    """Abstract interface for local quantum circuit simulators."""

    @abstractmethod
    def run(
        self,
        circuit: Any,
        *,
        shots: Optional[int] = None,
        seed: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:  # pragma: no cover - interface
        """Simulate ``circuit`` and return a provider-agnostic result."""

    @staticmethod
    @lru_cache(maxsize=128)
    def _cached_dot(
        a_bytes: bytes,
        b_bytes: bytes,
        a_shape: Tuple[int, int],
        b_shape: Tuple[int, int],
        dtype: str,
    ) -> bytes:
        """Cache-heavy matrix multiplication in serialized form."""
        a = np.frombuffer(a_bytes, dtype=dtype).reshape(a_shape)
        b = np.frombuffer(b_bytes, dtype=dtype).reshape(b_shape)
        return (a @ b).tobytes()

    @classmethod
    def dot(cls, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Multiply ``a`` and ``b`` using vectorization with caching."""
        if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[0]:
            raise ValueError("incompatible matrices")
        dtype = str(a.dtype)
        res_bytes = cls._cached_dot(a.tobytes(), b.tobytes(), a.shape, b.shape, dtype)
        return np.frombuffer(res_bytes, dtype=dtype).reshape(a.shape[0], b.shape[1])
