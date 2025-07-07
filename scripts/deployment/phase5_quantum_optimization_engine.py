#!/usr/bin/env python3
"""Wrapper for the main quantum optimization engine.

This thin wrapper imports and executes the canonical implementation
located one directory up. Keeping the logic in a single place reduces
maintenance overhead.
"""
import os
import sys

# Ensure parent directory is on the path so imports work when run directly
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from phase5_quantum_optimization_engine import main

if __name__ == "__main__":
    main()

