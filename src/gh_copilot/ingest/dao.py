from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


class IngestDAO:
    """Lightweight helper to log ingest events to analytics.db."""

    def __init__(self, analytics_db: Path) -> None:
        self.analytics_db = analytics_db

    @contextmanager
    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.analytics_db)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=10000;")
        try:
            yield conn
        finally:
            conn.close()

    def log_event(
        self,
        *,
        kind: str,
        source: str,
        target_table: str,
        target_pk: int | None,
        status: str,
        sha256: str | None = None,
        metrics: dict | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> None:
        def _write(conn: sqlite3.Connection) -> None:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ingest_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_at TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    source TEXT NOT NULL,
                    target_table TEXT NOT NULL,
                    target_pk INTEGER,
                    status TEXT NOT NULL,
                    sha256 TEXT,
                    metrics_json TEXT
                )
                """
            )
            conn.execute(
                """
                INSERT INTO ingest_events (
                    occurred_at, kind, source, target_table, target_pk,
                    status, sha256, metrics_json
                ) VALUES (datetime('now'), ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    kind,
                    source,
                    target_table,
                    target_pk,
                    status,
                    sha256,
                    json.dumps(metrics or {}, ensure_ascii=False),
                ),
            )

        if connection is not None:
            _write(connection)
        else:
            with self._conn() as conn, conn:
                _write(conn)

