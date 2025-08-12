#!/usr/bin/env python3
"""Quantum Clustering File Organization
=======================================

This script groups files in a directory using a quantum kernel-based
clustering approach. File size and modification time are converted to a
two-dimensional feature space, and a
``FidelityQuantumKernel`` computes the similarity matrix used by
:class:`sklearn.cluster.KMeans`.

The example illustrates how quantum kernels can assist with file
classification and organization tasks.

MODERNIZED: Now uses modular quantum package for enhanced functionality
while maintaining backward compatibility.
"""

import sys

# Import from new modular package
from ghc_quantum.algorithms.clustering import QuantumClustering, main

# Provide legacy alias for tests
EnterpriseUtility = QuantumClustering

# This script now delegates to the modular implementation
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
