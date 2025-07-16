#!/usr/bin/env python3
"""QuantumAlgorithmsFunctional
==============================

Collection of functional quantum algorithms used across the
``gh_COPILOT`` toolkit. Each function returns useful performance
metrics in addition to computational results.

MODERNIZED: Now uses modular quantum package for enhanced functionality
while maintaining backward compatibility.
"""

import sys

# Import from new modular package  
from quantum.algorithms.functional import QuantumFunctional, main

# This script now delegates to the modular implementation
if __name__ == "__main__":  # pragma: no cover - manual execution
    success = main()
    sys.exit(0 if success else 1)