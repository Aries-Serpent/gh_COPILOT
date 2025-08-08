#!/usr/bin/env python3
<<<<<<< HEAD
"""
Quantum-inspired processing components for gh_COPILOT Toolkit.

MODERNIZED: Enhanced with modular algorithm architecture, unified registry,
and orchestration capabilities while maintaining backward compatibility.
"""

from . import benchmarking, quantum_optimization
from .quantum_database_search import (
    quantum_search_sql,
    quantum_search_nosql,
    quantum_search_hybrid,
)
from .optimizers.quantum_optimizer import QuantumOptimizer

# Import new modular components
from .algorithms.base import QuantumAlgorithmBase
from .algorithms.clustering import QuantumClustering
from .algorithms.functional import QuantumFunctional
from .algorithms.expansion import QuantumLibraryExpansion
from .orchestration.registry import QuantumAlgorithmRegistry, get_global_registry
from .orchestration.executor import QuantumExecutor
from .quantum_integration_orchestrator import QuantumIntegrationOrchestrator

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
    "QuantumIntegrationOrchestrator",
    "QuantumOptimizer",
=======
"""Quantum-inspired processing components for gh_COPILOT Toolkit."""

from . import benchmarking, quantum_optimization
import logging

__all__ = [
    "benchmarking",
    "quantum_optimization",
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
]
