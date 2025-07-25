#!/usr/bin/env python3
"""Wrapper for :mod:`quantum.quantum_database_search` utilities."""
from quantum.quantum_database_search import (
    main,
    quantum_search_hybrid,
    quantum_search_nosql,
    quantum_search_sql,
)

__all__ = [
    "quantum_search_sql",
    "quantum_search_nosql",
    "quantum_search_hybrid",
    "main",
]

if __name__ == "__main__":  # pragma: no cover
    main()
