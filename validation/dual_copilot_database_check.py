"""Validation script demonstrating database-first operations and dual-copilot checks."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Tuple

from scripts.validation.dual_copilot_orchestrator import DualCopilotOrchestrator

PRODUCTION_DB = Path("databases/production.db")


def _database_has_tables() -> bool:
    if not PRODUCTION_DB.exists():
        return False
    with sqlite3.connect(PRODUCTION_DB) as conn:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return len(cur.fetchall()) > 0


def run_validation(timeout_minutes: int = 5) -> Tuple[bool, bool]:
    orchestrator = DualCopilotOrchestrator()
    primary = _database_has_tables
    return orchestrator.run(primary, [str(PRODUCTION_DB)], timeout_minutes)


if __name__ == "__main__":
    success, validated = run_validation()
    print(f"Primary success: {success}")
    print(f"Secondary success: {validated}")

