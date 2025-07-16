#!/usr/bin/env python3
"""
Quantum-inspired processing components for gh_COPILOT Toolkit.

MODERNIZED: Enhanced with modular algorithm architecture, unified registry,
and orchestration capabilities while maintaining backward compatibility.
"""

from . import benchmarking, quantum_optimization

# Import new modular components
from .algorithms.base import QuantumAlgorithmBase
from .algorithms.clustering import QuantumClustering
from .algorithms.functional import QuantumFunctional
from .algorithms.expansion import QuantumLibraryExpansion
from .orchestration.registry import QuantumAlgorithmRegistry, get_global_registry
from .orchestration.executor import QuantumExecutor

import logging

__version__ = "2.0.0"

__all__ = [
    "benchmarking",
    "quantum_optimization",
    # New modular components
    "QuantumAlgorithmBase",
    "QuantumClustering", 
    "QuantumFunctional",
    "QuantumLibraryExpansion",
    "QuantumAlgorithmRegistry",
    "get_global_registry",
    "QuantumExecutor",
]
