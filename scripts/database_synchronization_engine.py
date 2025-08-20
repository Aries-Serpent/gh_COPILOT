"""Simple SQLite database synchronization engine.

This module provides a lightweight synchronization utility that copies
data from a source SQLite database to a target database. It performs
basic schema mapping, resolves update conflicts using timestamp fields
and emits log records for each operation.  A ``log_hook`` callback can
be provided to observe log messages in real time.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Callable, Dict

# ---------------------------------------------------------------------------
# Schema mapping
# ---------------------------------------------------------------------------
# Only a minimal set of tables/columns are defined as the tests require. The
# mapping can be extended by callers for additional databases.
DATABASE_SCHEMA_MAP: Dict[str, Dict[str, str]] = {
    "production.db": {
        "generated_solutions": (
            "id INTEGER PRIMARY KEY, objective TEXT, template_name TEXT, "
            "code TEXT, session_id TEXT, created_at TEXT"
        ),
    },
    "analytics.db": {
        "sync_audit_log": ("id INTEGER PRIMARY KEY, source_db TEXT, target_db TEXT, action TEXT, timestamp INTEGER"),
    },
    "auxiliary.db": {},
}

LogHook = Callable[[str, str], None]


class DatabaseSynchronizationEngine:
    """Synchronize SQLite databases with simple conflict resolution."""

    def __init__(
        self,
        schema_map: Dict[str, Dict[str, str]] | None = None,
        *,
        log_path: Path | str = Path("logs/synchronization.log"),
        log_hook: LogHook | None = None,
    ) -> None:
        self.schema_map = schema_map or DATABASE_SCHEMA_MAP
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_hook = log_hook

        self._logger = logging.getLogger("database_synchronization")
        self._logger.setLevel(logging.INFO)

        # Replace existing handlers so each instance can specify its own log
        # destination during tests.
        for handler in list(self._logger.handlers):
            self._logger.removeHandler(handler)

        handler = logging.FileHandler(self.log_path, delay=True)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        self._logger.addHandler(handler)

    # ------------------------------------------------------------------
    # Logging helper
    # ------------------------------------------------------------------
    def _emit(self, level: int, message: str) -> None:
        self._logger.log(level, message)
        if self.log_hook:
            try:
                self.log_hook(logging.getLevelName(level).lower(), message)
            except Exception:  # pragma: no cover - hook failures are logged
                self._logger.exception("log_hook_error")

    # ------------------------------------------------------------------
    # Core synchronization logic
    # ------------------------------------------------------------------
    def sync(self, source: Path | str, target: Path | str) -> None:
        """Synchronize data from ``source`` SQLite database to ``target``."""

        source_path = Path(source)
        target_path = Path(target)
        self._emit(logging.INFO, f"sync_start {source_path} -> {target_path}")

        with sqlite3.connect(source_path) as src, sqlite3.connect(target_path) as tgt:
            src.row_factory = sqlite3.Row
            tgt.row_factory = sqlite3.Row

            tables = [r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            for table in tables:
                schema_sql = src.execute(
                    "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                    (table,),
                ).fetchone()[0]
                self._ensure_table(schema_sql=schema_sql, table=table, conn=tgt)

                src_rows: Dict[Any, Dict[str, Any]] = {
                    row["id"]: dict(row) for row in src.execute(f"SELECT * FROM {table}")
                }
                tgt_rows: Dict[Any, Dict[str, Any]] = {
                    row["id"]: dict(row) for row in tgt.execute(f"SELECT * FROM {table}")
                }

                for pk, srow in src_rows.items():
                    if pk not in tgt_rows:
                        self._insert_row(tgt, table, srow)
                        self._emit(logging.INFO, f"insert {table}:{pk}")
                        continue

                    trow = tgt_rows[pk]
                    src_ts = srow.get("updated_at") or srow.get("modified_at")
                    tgt_ts = trow.get("updated_at") or trow.get("modified_at")
                    if src_ts and tgt_ts and src_ts > tgt_ts:
                        self._update_row(tgt, table, srow)
                        self._emit(logging.INFO, f"update {table}:{pk}")
                    else:
                        self._emit(logging.INFO, f"conflict_skip {table}:{pk}")

                for pk in set(tgt_rows) - set(src_rows):
                    tgt.execute(f"DELETE FROM {table} WHERE id=?", (pk,))
                    self._emit(logging.INFO, f"delete {table}:{pk}")

            tgt.commit()

        self._emit(logging.INFO, f"sync_complete {source_path} -> {target_path}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _ensure_table(*, schema_sql: str, table: str, conn: sqlite3.Connection) -> None:
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,),
        ).fetchone()
        if not exists:
            conn.execute(schema_sql)

    @staticmethod
    def _insert_row(conn: sqlite3.Connection, table: str, row: Dict[str, Any]) -> None:
        cols = ", ".join(row.keys())
        placeholders = ", ".join("?" for _ in row)
        conn.execute(
            f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
            tuple(row.values()),
        )

    @staticmethod
    def _update_row(conn: sqlite3.Connection, table: str, row: Dict[str, Any]) -> None:
        cols = [c for c in row.keys() if c != "id"]
        assignments = ", ".join(f"{c}=?" for c in cols)
        values = [row[c] for c in cols] + [row["id"]]
        conn.execute(
            f"UPDATE {table} SET {assignments} WHERE id=?",
            values,
        )


def sync_databases(source: Path | str, target: Path | str) -> None:
    """Convenience wrapper to run a one-off synchronization."""

    engine = DatabaseSynchronizationEngine()
    engine.sync(source, target)
