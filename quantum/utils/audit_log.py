"""Utility helpers for recording quantum routine executions.

This module logs quantum algorithm runs to ``databases/analytics.db``.  It
creates the ``quantum_audit_log`` table on demand and stores hashes of the
input and output data for traceability.  Logging silently fails if the
analytics database is absent or unwritable so that quantum routines remain
non-blocking in constrained environments.
"""

from __future__ import annotations

import hashlib
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from enterprise_modules.compliance import (
    anti_recursion_guard,
    validate_enterprise_operation,
)

ANALYTICS_DB = Path("databases/analytics.db")


def _hash_payload(payload: Any) -> str:
    """Return a stable SHA256 hash for ``payload``."""

    return hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()


@anti_recursion_guard
def log_quantum_audit(
    algorithm_used: str, input_data: Any, output_data: Any, *, compliance_validated: bool = False
) -> None:
    """Record a quantum algorithm execution in ``quantum_audit_log``.

    Parameters
    ----------
    algorithm_used:
        Name of the quantum routine executed.
    input_data:
        Arbitrary data structure representing the input to the routine.
    output_data:
        Data structure representing the routine output.
    compliance_validated:
        Whether additional compliance checks were performed.
    """

    if not ANALYTICS_DB.exists():  # Database is optional in test environments
        return
    if not validate_enterprise_operation(str(ANALYTICS_DB)):
        raise RuntimeError("Invalid target path")

    try:
        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS quantum_audit_log (
                    operation_id TEXT PRIMARY KEY,
                    algorithm_used TEXT,
                    input_hash TEXT,
                    output_hash TEXT,
                    execution_time TEXT,
                    compliance_validated INTEGER
                )
                """
            )
            conn.execute(
                "INSERT INTO quantum_audit_log VALUES (?, ?, ?, ?, ?, ?)",
                (
                    str(uuid.uuid4()),
                    algorithm_used,
                    _hash_payload(input_data),
                    _hash_payload(output_data),
                    datetime.utcnow().isoformat(),
                    int(compliance_validated),
                ),
            )
            conn.commit()
    except sqlite3.Error:
        # Logging failures should not break algorithm execution
        return


__all__ = ["log_quantum_audit"]
