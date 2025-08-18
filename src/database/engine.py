"""Realtime SQLite change listeners with bidirectional sync."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from threading import Lock
from time import perf_counter
from typing import Any, Callable, Dict, List, Tuple

from src.schema.schema_mapper import SchemaMapper


logger = logging.getLogger(__name__)


class ChangeStream:
    """Manage change listeners for database triggers."""

    def __init__(self) -> None:
        self._listeners: List[Callable[[str, str, Dict[str, Any]], None]] = []
        self._lock = Lock()

    def register(self, callback: Callable[[str, str, Dict[str, Any]], None]) -> None:
        """Register a callback receiving (operation, table, row)."""

        with self._lock:
            self._listeners.append(callback)

    def notify(self, operation: str, table: str, row: Dict[str, Any]) -> None:
        with self._lock:
            listeners = list(self._listeners)
        for callback in listeners:
            callback(operation, table, row)


class Engine:
    """SQLite engine with change-stream triggers and bidirectional sync."""

    def __init__(
        self,
        path: Path | str,
        mapper: SchemaMapper | None = None,
        *,
        log_queries: bool = False,
    ) -> None:
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.stream = ChangeStream()
        self.mapper = mapper or SchemaMapper({})
        self.conn.create_function("notify_change", 3, self._notify_change)
        self.log_queries = log_queries
        self._conn_lock = Lock()

    # ------------------------------------------------------------------
    # change stream handling
    def _notify_change(self, operation: str, table: str, rowid: int) -> None:
        row = self.execute(f"SELECT * FROM {table} WHERE id=?", (rowid,)).fetchone()
        payload = dict(row) if row else {"id": rowid}
        self.stream.notify(operation, table, payload)

    def install_triggers(self, table: str) -> None:
        """Install change-stream triggers for ``table``."""

        self.execute(
            f"""
            CREATE TRIGGER IF NOT EXISTS {table}_notify_insert
            AFTER INSERT ON {table}
            BEGIN
                SELECT notify_change('insert', '{table}', NEW.id);
            END;
            """
        )
        self.execute(
            f"""
            CREATE TRIGGER IF NOT EXISTS {table}_notify_update
            AFTER UPDATE ON {table}
            BEGIN
                SELECT notify_change('update', '{table}', NEW.id);
            END;
            """
        )
        self.execute(
            f"""
            CREATE TRIGGER IF NOT EXISTS {table}_notify_delete
            AFTER DELETE ON {table}
            BEGIN
                SELECT notify_change('delete', '{table}', OLD.id);
            END;
            """
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    # synchronization
    def _resolve_conflict(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """Use ``SchemaMapper`` to resolve conflicting rows."""

        mapper = SchemaMapper(dict(a))
        if b.get("updated_at", 0) > a.get("updated_at", 0):
            return mapper.apply(b, strategy="overwrite")
        return a

    @staticmethod
    def _upsert(conn: sqlite3.Connection, table: str, row: Dict[str, Any]) -> None:
        columns = ", ".join(row.keys())
        placeholders = ", ".join(["?"] * len(row))
        updates = ", ".join([f"{c}=excluded.{c}" for c in row.keys()])
        conn.execute(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) "
            f"ON CONFLICT(id) DO UPDATE SET {updates}",
            tuple(row.values()),
        )

    def sync_with(self, other: "Engine") -> None:
        """Bidirectionally synchronize this engine with ``other``."""

        tables_self = {
            r[0] for r in self.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        tables_other = {
            r[0] for r in other.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        for table in tables_self | tables_other:
            rows_self = (
                {row["id"]: dict(row) for row in self.execute(f"SELECT * FROM {table}")}
                if table in tables_self
                else {}
            )
            rows_other = (
                {row["id"]: dict(row) for row in other.execute(f"SELECT * FROM {table}")}
                if table in tables_other
                else {}
            )
            for pk in rows_self.keys() | rows_other.keys():
                in_self = pk in rows_self
                in_other = pk in rows_other
                if in_self and in_other:
                    if rows_self[pk] != rows_other[pk]:
                        merged = self._resolve_conflict(rows_self[pk], rows_other[pk])
                        self._upsert(self.conn, table, merged)
                        self._upsert(other.conn, table, merged)
                elif in_self:
                    self._upsert(other.conn, table, rows_self[pk])
                else:
                    self._upsert(self.conn, table, rows_other[pk])
        self.conn.commit()
        other.conn.commit()

    # ------------------------------------------------------------------
    # utility helpers
    def execute(self, sql: str, params: Tuple[Any, ...] | None = None) -> sqlite3.Cursor:
        """Execute ``sql`` while optionally logging its duration."""

        with self._conn_lock:
            start = perf_counter()
            cur = self.conn.execute(sql, params or ())
            duration = perf_counter() - start
        if self.log_queries:
            logger.info("SQL %.6f %s", duration, sql)
        return cur

    def ensure_index(self, table: str, column: str) -> None:
        """Create an index on ``table`` for ``column`` if missing."""

        self.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{table}_{column} ON {table} ({column})"
        )
        self.conn.commit()

