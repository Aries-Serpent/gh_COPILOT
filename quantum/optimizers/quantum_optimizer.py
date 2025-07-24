"""Wrapper around :class:`quantum.utils.PerformanceOptimizer`."""
import logging
from ..utils import PerformanceOptimizer


class QuantumOptimizer(PerformanceOptimizer):
    """Performance optimizer with enterprise logging."""

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("[INFO] QuantumOptimizer initialized")

__all__ = ["QuantumOptimizer"]
