#!/usr/bin/env python3
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
    quantum_join_sql,
)
from .optimizers.quantum_optimizer import QuantumOptimizer
from .hybrid_database_processor import QuantumDatabaseProcessor
from .next_generation_ai import NextGenerationAI

# Import new modular components
from .algorithms.base import QuantumAlgorithmBase
from .algorithms.clustering import QuantumClustering
from .algorithms.functional import QuantumFunctional
from .algorithms.expansion import QuantumLibraryExpansion
from .orchestration.registry import QuantumAlgorithmRegistry, get_global_registry
from .orchestration.executor import QuantumExecutor
from .quantum_integration_orchestrator import QuantumIntegrationOrchestrator
from .quantum_data_pipeline import QuantumDataPipeline
from .quantum_algorithm_library_expansion import advanced_grover_search, advanced_vqe

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
    "QuantumDatabaseProcessor",
    "NextGenerationAI",
    "QuantumOptimizer",
    "QuantumDataPipeline",
    "quantum_join_sql",
    "advanced_grover_search",
    "advanced_vqe",
]
