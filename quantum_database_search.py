"""Wrapper for :mod:`quantum.quantum_database_search` functions."""
from quantum.quantum_database_search import (
    quantum_search_hybrid,
    quantum_search_nosql,
    quantum_search_sql,
)

__all__ = [
    "quantum_search_sql",
    "quantum_search_nosql",
    "quantum_search_hybrid",
]
