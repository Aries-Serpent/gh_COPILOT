#!/usr/bin/env python3
"""Wrapper for quantum optimization refinement utilities.

Imports the main refinement module from the parent directory to avoid
maintaining duplicate logic.
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from quantum_optimization_refinement import main

if __name__ == "__main__":
    main()

