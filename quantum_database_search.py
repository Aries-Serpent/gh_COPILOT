#!/usr/bin/env python3
"""Wrapper for :mod:`ghc_quantum.quantum_database_search` utilities."""

from utils.cross_platform_paths import verify_environment_variables

__all__ = [
    "quantum_search_sql",
    "quantum_search_nosql",
    "quantum_search_hybrid",
    "quantum_secure_search",
    "cli",
]


def quantum_search_sql(*args, **kwargs):
    """Lazy import and execute ``quantum_search_sql``."""
    from ghc_quantum.quantum_database_search import quantum_search_sql as _func

    return _func(*args, **kwargs)


def quantum_search_nosql(*args, **kwargs):
    """Lazy import and execute ``quantum_search_nosql``."""
    from ghc_quantum.quantum_database_search import quantum_search_nosql as _func

    return _func(*args, **kwargs)


def quantum_search_hybrid(*args, **kwargs):
    """Lazy import and execute ``quantum_search_hybrid``."""
    from ghc_quantum.quantum_database_search import quantum_search_hybrid as _func

    return _func(*args, **kwargs)


def quantum_secure_search(*args, **kwargs):
    """Lazy import and execute ``quantum_secure_search``."""
    from ghc_quantum.quantum_database_search import quantum_secure_search as _func

    return _func(*args, **kwargs)


def cli() -> None:
    """Run :mod:`quantum.quantum_database_search` CLI after environment check."""
    verify_environment_variables()
    from ghc_quantum.quantum_database_search import main

    main()


if __name__ == "__main__":  # pragma: no cover
    cli()
