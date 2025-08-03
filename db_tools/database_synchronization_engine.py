"""Database synchronization utilities."""

from __future__ import annotations

import logging
import sqlite3
import threading
import time
from pathlib import Path
from typing import Dict, Any


# Schema mapping for known databases. Each database maps table names to simple
# column definitions. The mapping intentionally includes only the minimal
# fields required for synchronization tests.
DATABASE_SCHEMA_MAP: Dict[str, Dict[str, str]] = {
    "production.db": {
        "generated_solutions": "id INTEGER PRIMARY KEY, content TEXT, updated_at INTEGER",
    },
    "analytics.db": {
        "sync_audit_log": (
            "id INTEGER PRIMARY KEY, source_db TEXT, target_db TEXT, "
            "action TEXT, timestamp INTEGER"
        ),
    },
    "auxiliary.db": {},
}


class DatabaseSynchronizationEngine:
    """Synchronize SQLite databases with basic conflict resolution."""

    def __init__(self, schema_map: Dict[str, Dict[str, str]] | None = None, *, log_path: Path | str = Path("logs/synchronization.log")) -> None:
        self.schema_map = schema_map or DATABASE_SCHEMA_MAP
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        self._logger = logging.getLogger("database_synchronization")
        self._logger.setLevel(logging.INFO)
        handler = logging.FileHandler(self.log_path, delay=True)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        if not self._logger.handlers:
            self._logger.addHandler(handler)

        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Real-time synchronization
    # ------------------------------------------------------------------
    def start_realtime_sync(self, source: Path | str, target: Path | str, *, interval: float = 1.0) -> None:
        """Start a background thread that periodically synchronizes databases."""

        source_path = Path(source)
        target_path = Path(target)

        def _worker() -> None:
            while not self._stop_event.is_set():
                try:
                    self.sync(source_path, target_path)
                except Exception as exc:  # pragma: no cover - logged for visibility
                    self._logger.error("sync_error %s", exc)
                time.sleep(interval)

        threading.Thread(target=_worker, daemon=True).start()

    def stop_realtime_sync(self) -> None:
        """Stop the background synchronization thread."""

        self._stop_event.set()

    # ------------------------------------------------------------------
    # Core synchronization logic
    # ------------------------------------------------------------------
    def sync(self, source: Path | str, target: Path | str) -> None:
        """Synchronize data from ``source`` SQLite database to ``target``."""

        source_path = Path(source)
        target_path = Path(target)
        self._logger.info("sync_start %s -> %s", source_path, target_path)

        with sqlite3.connect(source_path) as src, sqlite3.connect(target_path) as tgt:
            src.row_factory = sqlite3.Row
            tgt.row_factory = sqlite3.Row

            tables = [r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            for table in tables:
                self._ensure_table(schema_sql=src.execute(
                    "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                    (table,),
                ).fetchone()[0], table=table, conn=tgt)

                src_rows: Dict[Any, Dict[str, Any]] = {row["id"]: dict(row) for row in src.execute(f"SELECT * FROM {table}")}
                tgt_rows: Dict[Any, Dict[str, Any]] = {row["id"]: dict(row) for row in tgt.execute(f"SELECT * FROM {table}")}

                for pk, srow in src_rows.items():
                    if pk not in tgt_rows:
                        self._insert_row(tgt, table, srow)
                        self._logger.info("insert %s:%s", table, pk)
                        continue

                    trow = tgt_rows[pk]
                    src_ts = srow.get("updated_at") or srow.get("modified_at")
                    tgt_ts = trow.get("updated_at") or trow.get("modified_at")
                    if src_ts and tgt_ts and src_ts > tgt_ts:
                        self._update_row(tgt, table, srow)
                        self._logger.info("update %s:%s", table, pk)
                    else:
                        self._logger.info("conflict_skip %s:%s", table, pk)

                for pk in set(tgt_rows) - set(src_rows):
                    tgt.execute(f"DELETE FROM {table} WHERE id=?", (pk,))
                    self._logger.info("delete %s:%s", table, pk)

            tgt.commit()

        self._logger.info("sync_complete %s -> %s", source_path, target_path)

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


def sync_databases(source: str | Path, target: str | Path) -> None:
    """Backwards compatible helper to run a one-off synchronization."""

    engine = DatabaseSynchronizationEngine()
    engine.sync(source, target)

