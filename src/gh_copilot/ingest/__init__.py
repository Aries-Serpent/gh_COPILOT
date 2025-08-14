"""
Re-export stable ingestion entrypoints.

This merged initializer:
- Exposes ingest_har_entries & IngestResult from .har (or local ingest module variant).
- Conditionally exposes IngestDAO if available.
"""

from __future__ import annotations

try:
    from .har import ingest_har_entries, IngestResult  # type: ignore
except Exception:
    # Fallback: attempt sibling module name variant
    try:
        from .ingest_har_entries import ingest_har_entries, IngestResult  # type: ignore
    except Exception:
        ingest_har_entries = None  # type: ignore
        IngestResult = None  # type: ignore

try:
    from .dao import IngestDAO  # type: ignore
except Exception:
    IngestDAO = None  # type: ignore

__all__ = [" ingest_har_entries", "IngestResult"]
if IngestDAO:
    __all__.append("IngestDAO")
