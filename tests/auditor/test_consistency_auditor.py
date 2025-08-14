from __future__ import annotations

import sqlite3
from pathlib import Path

from gh_copilot.auditor.consistency import run_audit


def _mk_db(p: Path) -> sqlite3.Connection:
    c = sqlite3.connect(p)
    c.execute("PRAGMA journal_mode=WAL;")
    c.execute("PRAGMA busy_timeout=10000;")
    return c


def test_audit_minimal(tmp_path: Path) -> None:
    ent = tmp_path / "enterprise_assets.db"
    prod = tmp_path / "production.db"
    ana = tmp_path / "analytics.db"

    with _mk_db(ent) as c:
        # Create documentation_assets table and insert a README.md record
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS documentation_assets(
              id INTEGER PRIMARY KEY, path TEXT NOT NULL, content_hash TEXT
            )
            """
        )
        c.execute(
            "INSERT INTO documentation_assets(path, content_hash) VALUES(?, 'abc')",
            (str(tmp_path / "README.md"),),
        )
    with _mk_db(prod) as c:
        # Create har_entries table and insert a missing.har record
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS har_entries(
              id INTEGER PRIMARY KEY, path TEXT NOT NULL, sha256 TEXT
            )
            """
        )
        c.execute(
            "INSERT INTO har_entries(path, sha256) VALUES(?, 'def')",
            (str(tmp_path / "missing.har"),),
        )
    with _mk_db(ana) as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS consistency_audit_events(
              id INTEGER PRIMARY KEY, started_at TEXT, finished_at TEXT,
              scanned_paths TEXT, missing_count INTEGER, stale_count INTEGER,
              regenerated_count INTEGER, reingested_count INTEGER,
              details_json TEXT, status TEXT
            );
            """
        )

    (tmp_path / "README.md").write_text("changed", encoding="utf-8")

    res = run_audit(ent, prod, ana, [tmp_path], ["*.md"])
    assert res.missing_count >= 1
    assert res.stale_count >= 1

__all__ = [
    "test_audit_minimal",
    "_mk_db",
]
