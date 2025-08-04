"""Bidirectional database synchronization utilities.

This module provides two main classes:

``SchemaMapper``
    Ensures tables present in one database exist in the other.

``SyncManager``
    Performs bidirectional synchronization using explicit transactions and
    pluggable conflict-resolution callbacks.  Each call to :meth:`SyncManager.sync`
    records an event in ``analytics.db`` under the ``synchronization_events``
    table.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Callable, Dict, Any


class SchemaMapper:
    """Map tables between two SQLite databases."""

    def map(self, source: sqlite3.Connection, target: sqlite3.Connection) -> None:
        """Ensure tables from ``source`` exist in ``target``."""

        for name, sql in source.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table'"
        ):
            exists = target.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (name,),
            ).fetchone()
            if not exists:
                target.execute(sql)


class SyncManager:
    """Synchronize two SQLite databases in both directions."""

    def __init__(
        self,
        mapper: SchemaMapper | None = None,
        *,
        analytics_db: Path | str = Path("databases/analytics.db"),
    ) -> None:
        self.mapper = mapper or SchemaMapper()
        self.analytics_db = Path(analytics_db)

    def sync(
        self,
        db_a: Path | str,
        db_b: Path | str,
        resolver: Callable[[str, Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
        | None = None,
    ) -> None:
        """Bidirectionally synchronize ``db_a`` and ``db_b``.

        ``resolver`` is invoked when a row exists in both databases with the same
        primary key but differing content.  It receives ``(table, row_a, row_b)``
        and must return the row that should be kept.
        """

        db_a = Path(db_a)
        db_b = Path(db_b)
        resolver = resolver or self._default_resolver

        with sqlite3.connect(db_a) as conn_a, sqlite3.connect(db_b) as conn_b:
            conn_a.row_factory = sqlite3.Row
            conn_b.row_factory = sqlite3.Row
            conn_a.execute("BEGIN")
            conn_b.execute("BEGIN")
            try:
                self.mapper.map(conn_a, conn_b)
                self.mapper.map(conn_b, conn_a)

                tables_a = {
                    r[0] for r in conn_a.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                tables_b = {
                    r[0] for r in conn_b.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                tables = tables_a | tables_b

                for table in tables:
                    rows_a = {
                        row["id"]: dict(row)
                        for row in conn_a.execute(f"SELECT * FROM {table}")
                    }
                    rows_b = {
                        row["id"]: dict(row)
                        for row in conn_b.execute(f"SELECT * FROM {table}")
                    }

                    for pk in rows_a.keys() | rows_b.keys():
                        in_a = pk in rows_a
                        in_b = pk in rows_b
                        if in_a and in_b:
                            row = rows_a[pk]
                            other = rows_b[pk]
                            if row != other:
                                merged = resolver(table, row, other)
                                self._upsert(conn_a, table, merged)
                                self._upsert(conn_b, table, merged)
                        elif in_a:
                            self._upsert(conn_b, table, rows_a[pk])
                        else:
                            self._upsert(conn_a, table, rows_b[pk])

                conn_a.commit()
                conn_b.commit()
            except Exception:
                conn_a.rollback()
                conn_b.rollback()
                self._log_event(db_a, db_b, "sync_failed")
                raise
            else:
                self._log_event(db_a, db_b, "sync")

    @staticmethod
    def _upsert(conn: sqlite3.Connection, table: str, row: Dict[str, Any]) -> None:
        cols = ", ".join(row.keys())
        placeholders = ", ".join("?" for _ in row)
        conn.execute(
            f"REPLACE INTO {table} ({cols}) VALUES ({placeholders})",
            tuple(row.values()),
        )

    @staticmethod
    def _default_resolver(
        table: str, row_a: Dict[str, Any], row_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        ts_a = row_a.get("updated_at") or row_a.get("modified_at") or 0
        ts_b = row_b.get("updated_at") or row_b.get("modified_at") or 0
        return row_a if ts_a >= ts_b else row_b

    def _log_event(self, db_a: Path, db_b: Path, action: str) -> None:
        self.analytics_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS synchronization_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_db TEXT NOT NULL,
                    target_db TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                "INSERT INTO synchronization_events (source_db, target_db, action, timestamp)"
                " VALUES (?, ?, ?, strftime('%s','now'))",
                (str(db_a), str(db_b), action),
            )
            conn.commit()


__all__ = ["SchemaMapper", "SyncManager"]

