"""Bidirectional database synchronization utilities and enterprise processor.

This module provides:

SchemaMapper
    Ensures tables present in one SQLite database exist in the other.

SyncManager
    Performs bidirectional synchronization using explicit transactions and
    pluggable conflict-resolution policies. Synchronization results and
    conflicts are recorded in an analytics database (analytics.db by default).

SyncWatcher
    Observes one or more database pairs and triggers SyncManager.sync when changes
    are detected.

EnterpriseDatabaseProcessor
    A generic, enterprise-style database processing runner with structured logging.

Additionally, helper functions are provided:
- watch_and_sync: Watch two databases and synchronize automatically.
- list_events: Read recent synchronization events from the analytics database.
"""

from __future__ import annotations

import logging
import re
import sqlite3
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

_TABLE_RE = re.compile(r"^[A-Za-z0-9_]+$")


def sanitize_table_name(name: str) -> str:
    """Return name if it is a valid table identifier, else raise ValueError.

    Only alphanumeric characters and underscores are allowed.
    This prevents SQL injection via table identifiers.
    """
    if not _TABLE_RE.fullmatch(name):
        raise ValueError(f"Invalid table name: {name!r}")
    return name


# ---------------------------------------------------------------------------
# Schema mapping
# ---------------------------------------------------------------------------

class SchemaMapper:
    """Map tables between two SQLite databases."""

    def map(self, source: sqlite3.Connection, target: sqlite3.Connection) -> None:
        """Ensure tables from source exist in target by replaying CREATE TABLE."""
        for name, sql in source.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table'"
        ):
            exists = target.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (name,),
            ).fetchone()
            if not exists and sql:
                target.execute(sql)


# ---------------------------------------------------------------------------
# Conflict resolution policies
# ---------------------------------------------------------------------------

class ConflictPolicy:
    """Base class for conflict resolution policies."""

    def resolve(
        self,
        table: str,
        row_a: Dict[str, Any],
        row_b: Dict[str, Any],
    ) -> Dict[str, Any]:  # pragma: no cover - interface
        raise NotImplementedError


class ResolverPolicy(ConflictPolicy):
    """Wrap a simple resolver callable into a ConflictPolicy."""

    def __init__(
        self,
        resolver: Callable[[str, Dict[str, Any], Dict[str, Any]], Dict[str, Any]],
    ) -> None:
        self._resolver = resolver

    def resolve(
        self,
        table: str,
        row_a: Dict[str, Any],
        row_b: Dict[str, Any],
    ) -> Dict[str, Any]:
        return self._resolver(table, row_a, row_b)


class TimestampConflictPolicy(ConflictPolicy):
    """Choose the row with the newest timestamp."""

    def resolve(
        self,
        table: str,
        row_a: Dict[str, Any],
        row_b: Dict[str, Any],
    ) -> Dict[str, Any]:
        ts_a = row_a.get("updated_at") or row_a.get("modified_at") or 0
        ts_b = row_b.get("updated_at") or row_b.get("modified_at") or 0
        return row_a if ts_a >= ts_b else row_b


class LastWriteWinsPolicy(TimestampConflictPolicy):
    """Resolve conflicts by keeping the row with the latest timestamp."""


# ---------------------------------------------------------------------------
# Synchronization manager and watcher
# ---------------------------------------------------------------------------

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
        *,
        resolver: Callable[[str, Dict[str, Any], Dict[str, Any]], Dict[str, Any]] | None = None,
        policy: ConflictPolicy | str | None = None,
        resolver_registry: Dict[
            str, Callable[[str, Dict[str, Any], Dict[str, Any]], Dict[str, Any]] | ConflictPolicy
        ] | None = None,
    ) -> None:
        """Bidirectionally synchronize db_a and db_b.

        Parameters:
            resolver: Deprecated; pass policy instead. Retained for backward compatibility.
            policy: A ConflictPolicy instance or the string "last-write-wins"/"timestamp".
            resolver_registry: Optional per-table resolvers or ConflictPolicy instances.

        On conflict, the chosen policy resolves differing rows.
        Events and conflicts are recorded in the analytics database.
        """
        db_a = Path(db_a)
        db_b = Path(db_b)

        # Allow string shortcuts for policies for convenience/back-compat
        if isinstance(policy, str):
            key = policy.lower()
            if key in {"last-write-wins", "timestamp"}:
                policy = LastWriteWinsPolicy()
            else:
                raise ValueError(f"Unknown conflict policy: {policy}")

        # Default policy falls back to legacy resolver if provided
        if policy is None:
            resolver = resolver or self._default_resolver
            policy = ResolverPolicy(resolver)

        with sqlite3.connect(db_a) as conn_a, sqlite3.connect(db_b) as conn_b:
            conn_a.row_factory = sqlite3.Row
            conn_b.row_factory = sqlite3.Row

            # Explicit transactions on both sides
            conn_a.execute("BEGIN")
            conn_b.execute("BEGIN")
            try:
                # Ensure schema parity in both directions
                self.mapper.map(conn_a, conn_b)
                self.mapper.map(conn_b, conn_a)

                # Enumerate tables
                tables_a = {
                    sanitize_table_name(r[0])
                    for r in conn_a.execute("SELECT name FROM sqlite_master WHERE type='table'")
                }
                tables_b = {
                    sanitize_table_name(r[0])
                    for r in conn_b.execute("SELECT name FROM sqlite_master WHERE type='table'")
                }
                tables = tables_a | tables_b

                for table in tables:
                    # Determine PK; continue only if primary key column is named "id"
                    conn_ref = conn_a if table in tables_a else conn_b
                    pk = self._get_primary_key(conn_ref, table)
                    if pk != "id":
                        continue

                    # Load all rows keyed by primary key
                    rows_a = {
                        row[pk]: dict(row)
                        for row in conn_a.execute(f'SELECT * FROM "{table}"')
                    }
                    rows_b = {
                        row[pk]: dict(row)
                        for row in conn_b.execute(f'SELECT * FROM "{table}"')
                    }

                    # Choose per-table policy if provided
                    table_policy: ConflictPolicy = policy
                    if resolver_registry and table in resolver_registry:
                        custom = resolver_registry[table]
                        table_policy = custom if isinstance(custom, ConflictPolicy) else ResolverPolicy(custom)

                    # Reconcile
                    for pk_val in rows_a.keys() | rows_b.keys():
                        in_a = pk_val in rows_a
                        in_b = pk_val in rows_b
                        if in_a and in_b:
                            row = rows_a[pk_val]
                            other = rows_b[pk_val]
                            if row != other:
                                merged = table_policy.resolve(table, row, other)
                                decision = "a" if merged == row else "b"
                                self._log_conflict(db_a, db_b, table, pk_val, decision)
                                self._upsert(conn_a, table, merged)
                                self._upsert(conn_b, table, merged)
                        elif in_a:
                            self._upsert(conn_b, table, rows_a[pk_val])
                        else:
                            self._upsert(conn_a, table, rows_b[pk_val])

                conn_a.commit()
                conn_b.commit()
            except Exception:
                # Roll back both sides to keep consistency
                conn_a.rollback()
                conn_b.rollback()
                self._log_event(db_a, db_b, "sync", "failure")
                raise
            else:
                self._log_event(db_a, db_b, "sync", "success")

    def watch(
        self,
        db_a: Path | str,
        db_b: Path | str,
        *,
        interval: float = 1.0,
        stop_event: threading.Event | None = None,
        resolver: Callable[[str, Dict[str, Any], Dict[str, Any]], Dict[str, Any]] | None = None,
        policy: ConflictPolicy | str | None = None,
        resolver_registry: Dict[
            str, Callable[[str, Dict[str, Any], Dict[str, Any]], Dict[str, Any]] | ConflictPolicy
        ] | None = None,
    ) -> None:
        """Watch databases for changes and synchronize on modification."""
        db_a = Path(db_a)
        db_b = Path(db_b)
        stop_event = stop_event or threading.Event()
        last_a = db_a.stat().st_mtime if db_a.exists() else 0
        last_b = db_b.stat().st_mtime if db_b.exists() else 0

        while not stop_event.is_set():
            try:
                mt_a = db_a.stat().st_mtime if db_a.exists() else 0
                mt_b = db_b.stat().st_mtime if db_b.exists() else 0
                if mt_a != last_a or mt_b != last_b:
                    self.sync(
                        db_a,
                        db_b,
                        resolver=resolver,
                        policy=policy,
                        resolver_registry=resolver_registry,
                    )
                    last_a, last_b = mt_a, mt_b
            except Exception:
                # Errors are already logged by sync; keep the watcher running.
                pass
            time.sleep(interval)

    @staticmethod
    def _get_primary_key(conn: sqlite3.Connection, table: str) -> str | None:
        """Return the name of the primary key column for table."""
        safe_table = sanitize_table_name(table)
        info = conn.execute(f'PRAGMA table_info("{safe_table}")').fetchall()
        for column in info:
            if column[5]:  # PK flag
                return column[1]
        return None

    @staticmethod
    def _upsert(conn: sqlite3.Connection, table: str, row: Dict[str, Any]) -> None:
        """Insert or replace a row into table."""
        safe_table = sanitize_table_name(table)
        cols = ", ".join(f'"{c}"' for c in row.keys())
        marks = ", ".join("?" for _ in row)
        conn.execute(
            f'REPLACE INTO "{safe_table}" ({cols}) VALUES ({marks})',
            tuple(row.values()),
        )

    @staticmethod
    def _default_resolver(table: str, row_a: Dict[str, Any], row_b: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy resolver: prefer the row with the latest timestamp."""
        ts_a = row_a.get("updated_at") or row_a.get("modified_at") or 0
        ts_b = row_b.get("updated_at") or row_b.get("modified_at") or 0
        return row_a if ts_a >= ts_b else row_b

    # Analytics logging -----------------------------------------------------

    def _log_event(self, db_a: Path, db_b: Path, action: str, status: str) -> None:
        """Log a synchronization event to the analytics database."""
        self.analytics_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS synchronization_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_db TEXT NOT NULL,
                    target_db TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp INTEGER NOT NULL
                )
                """,
            )
            conn.execute(
                "INSERT INTO synchronization_events (source_db, target_db, action, status, timestamp)"
                " VALUES (?, ?, ?, ?, strftime('%s','now'))",
                (str(db_a), str(db_b), action, status),
            )
            conn.commit()

    def _log_conflict(self, db_a: Path, db_b: Path, table: str, row_id: Any, decision: str) -> None:
        """Log a row-level conflict to the analytics database."""
        self.analytics_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS synchronization_conflicts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_db TEXT NOT NULL,
                    target_db TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    row_id INTEGER NOT NULL,
                    decision TEXT NOT NULL,
                    timestamp INTEGER NOT NULL
                )
                """,
            )
            # pk is enforced as "id" and generally integer; cast defensively
            try:
                row_id_int = int(row_id)
            except (TypeError, ValueError):
                # If cast fails, fall back to 0 to maintain schema; still record conflict.
                row_id_int = 0
            conn.execute(
                "INSERT INTO synchronization_conflicts (source_db, target_db, table_name, row_id, decision, timestamp)"
                " VALUES (?, ?, ?, ?, ?, strftime('%s','now'))",
                (str(db_a), str(db_b), table, row_id_int, decision),
            )
            conn.commit()


class SyncWatcher:
    """Watch multiple database pairs and synchronize on changes."""

    def __init__(self, manager: SyncManager | None = None) -> None:
        self.manager = manager or SyncManager()

    def watch_pairs(
        self,
        pairs: List[tuple[Path | str, Path | str]],
        *,
        interval: float = 1.0,
        stop_event: threading.Event | None = None,
        **kwargs: Any,
    ) -> None:
        """Watch each pair and trigger synchronization when modified.

        A thread is spawned for each database pair using SyncManager.watch.
        This method blocks until stop_event is set.
        """
        stop_event = stop_event or threading.Event()
        threads: List[threading.Thread] = []
        for db_a, db_b in pairs:
            thread = threading.Thread(
                target=self.manager.watch,
                args=(db_a, db_b),
                kwargs={"interval": interval, "stop_event": stop_event, **kwargs},
                daemon=True,
            )
            thread.start()
            threads.append(thread)

        try:
            while not stop_event.is_set():
                time.sleep(interval)
        finally:
            stop_event.set()
            for thread in threads:
                thread.join()


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def watch_and_sync(
    db_a: Path | str,
    db_b: Path | str,
    *,
    interval: float = 1.0,
    stop_event: threading.Event | None = None,
    manager: SyncManager | None = None,
    resolver: Callable[[str, Dict[str, Any], Dict[str, Any]], Dict[str, Any]] | None = None,
    policy: ConflictPolicy | str | None = None,
    resolver_registry: Dict[
        str, Callable[[str, Dict[str, Any], Dict[str, Any]], Dict[str, Any]] | ConflictPolicy
    ] | None = None,
) -> None:
    """Watch two databases for changes and synchronize automatically."""
    manager = manager or SyncManager()
    manager.watch(
        db_a,
        db_b,
        interval=interval,
        stop_event=stop_event,
        resolver=resolver,
        policy=policy,
        resolver_registry=resolver_registry,
    )


def list_events(analytics_db: Path | str, limit: int = 10) -> List[Dict[str, Any]]:
    """Return recent synchronization events from the analytics database."""
    events: List[Dict[str, Any]] = []
    db_path = Path(analytics_db)
    if not db_path.exists():
        return events
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "SELECT timestamp, source_db, target_db, action, status "
            "FROM synchronization_events "
            "ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        events = [
            {
                "timestamp": row[0],
                "source_db": row[1],
                "target_db": row[2],
                "action": row[3],
                "status": row[4],
            }
            for row in cur.fetchall()
        ]
    return events


# ---------------------------------------------------------------------------
# Enterprise processor (additional functionality merged from other branch)
# ---------------------------------------------------------------------------

# Text-based indicators (no emojis)
TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "database": "[DATABASE]",
    "info": "[INFO]",
}


class EnterpriseDatabaseProcessor:
    """Enterprise database processing system with structured logging."""

    def __init__(self, database_path: str = "production.db") -> None:
        self.database_path = Path(database_path)
        self.logger = logging.getLogger(__name__)

    def execute_processing(self) -> bool:
        """Execute database processing with commit/rollback semantics."""
        start_time = datetime.now()
        self.logger.info(f"{TEXT_INDICATORS['start']} Processing started: {start_time}")

        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Execute operations
                success = self.process_operations(cursor)

                if success:
                    conn.commit()
                    self.logger.info(f"{TEXT_INDICATORS['success']} Database processing completed")
                    return True
                else:
                    conn.rollback()
                    self.logger.error(f"{TEXT_INDICATORS['error']} Database processing failed")
                    return False

        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Database error: {e}")
            return False

    def process_operations(self, cursor: sqlite3.Cursor) -> bool:
        """Process database operations. Override with real logic."""
        try:
            # Placeholder for real operations
            return True
        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Operation failed: {e}")
            return False


def main() -> bool:
    """Main execution function for enterprise processor CLI."""
    # Basic logging configuration for CLI usage
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    processor = EnterpriseDatabaseProcessor()
    success = processor.execute_processing()

    if success:
        print(f"{TEXT_INDICATORS['success']} Database processing completed")
    else:
        print(f"{TEXT_INDICATORS['error']} Database processing failed")

    return success


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "SchemaMapper",
    "ConflictPolicy",
    "ResolverPolicy",
    "TimestampConflictPolicy",
    "LastWriteWinsPolicy",
    "SyncManager",
    "SyncWatcher",
    "watch_and_sync",
    "list_events",
    "sanitize_table_name",
    "EnterpriseDatabaseProcessor",
    "main",
]


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
    