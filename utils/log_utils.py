# [Utils]: Analytics Logging Utilities (TEST-ONLY analytics.db generation)
# > Generated: 2025-07-25 14:37:07 | Author: mbaetiong
# --- Enterprise Standards ---
# - Flake8/PEP8 Compliant
# - Visual Processing Indicators, Dual Copilot Pattern
# - Full database-first and anti-recursion compliance
# - Production logging writes directly to analytics.db
# - Streaming support for web dashboard via Server-Sent Events

import json
import logging
import os
import sqlite3
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

# ``tqdm`` is optional; provide a no-op fallback if unavailable.
try:  # pragma: no cover - import guard for optional dependency
    from tqdm import tqdm
except ModuleNotFoundError:  # pragma: no cover
    def tqdm(iterable=None, **kwargs):  # type: ignore[override]
        return iterable if iterable is not None else []

# Default analytics DB path (test-only, never created here)
DEFAULT_ANALYTICS_DB = Path(os.environ.get("ANALYTICS_DB", "databases/analytics.db"))
DEFAULT_LOG_TABLE = "event_log"
_log_lock = threading.Lock()

# Standard table schemas for analytics.db. These are used when real writes are
# explicitly requested. The tables mirror the SQL migrations under
# ``databases/migrations``.
TABLE_SCHEMAS: Dict[str, str] = {
    "violation_logs": """
        CREATE TABLE IF NOT EXISTS violation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event TEXT,
            details TEXT NOT NULL,
            cause TEXT,
            remediation_path TEXT,
            rollback_trigger TEXT,
            count INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_violation_logs_timestamp
            ON violation_logs(timestamp);
    """,
    "rollback_logs": """
        CREATE TABLE IF NOT EXISTS rollback_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            backup TEXT,
            violation_id INTEGER,
            outcome TEXT,
            event TEXT,
            count INTEGER,
            timestamp TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_rollback_logs_timestamp
            ON rollback_logs(timestamp);
    """,
    "correction_logs": """
        CREATE TABLE IF NOT EXISTS correction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            doc_id TEXT,
            path TEXT,
            asset_type TEXT,
            compliance_score REAL,
            timestamp TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_correction_logs_timestamp
            ON correction_logs(timestamp);
    """,
    "sync_events_log": """
        CREATE TABLE IF NOT EXISTS sync_events_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            target TEXT,
            ts TEXT
        );
    """,
    "audit_log": """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            db_name TEXT,
            details TEXT,
            ts TEXT
        );
    """,
    "event_log": """
        CREATE TABLE IF NOT EXISTS event_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            module TEXT,
            level TEXT,
            description TEXT,
            details TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_event_log_timestamp
            ON event_log(timestamp);
    """,
    "monitoring_cycles": """
        CREATE TABLE IF NOT EXISTS monitoring_cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            cpu_percent REAL,
            memory_percent REAL,
            anomaly INTEGER,
            note TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_monitoring_cycles_timestamp
            ON monitoring_cycles(timestamp);
    """,
    "corrections": """
        CREATE TABLE IF NOT EXISTS corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            rationale TEXT,
            correction_type TEXT,
            compliance_score REAL,
            compliance_delta REAL,
            rollback_reference TEXT,
            session_id TEXT,
            ts TEXT
        );
    """,
    "correction_history": """
        CREATE TABLE IF NOT EXISTS correction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_correction_history_user_id ON correction_history(user_id);
        CREATE INDEX IF NOT EXISTS idx_correction_history_session_id ON correction_history(session_id);
        CREATE INDEX IF NOT EXISTS idx_correction_history_file_path ON correction_history(file_path);
        CREATE INDEX IF NOT EXISTS idx_correction_history_timestamp ON correction_history(timestamp);
    """,
    "code_audit_history": """
        CREATE TABLE IF NOT EXISTS code_audit_history (
            id INTEGER PRIMARY KEY,
            audit_entry TEXT NOT NULL,
            user TEXT NOT NULL,
            timestamp TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_code_audit_history_timestamp ON code_audit_history(timestamp);
        CREATE INDEX IF NOT EXISTS idx_code_audit_history_user ON code_audit_history(user);
    """,
    "placeholder_removals": """
        CREATE TABLE IF NOT EXISTS placeholder_removals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placeholder TEXT,
            ts TEXT
        );
    """,
    "todo_fixme_tracking": """
        CREATE TABLE IF NOT EXISTS todo_fixme_tracking (
            file_path TEXT,
            line_number INTEGER,
            placeholder_type TEXT,
            context TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved BOOLEAN DEFAULT 0,
            resolved_timestamp DATETIME,
            status TEXT DEFAULT 'open',
            removal_id INTEGER REFERENCES placeholder_removals(id)
        );
    """,
    "size_violations": """
        CREATE TABLE IF NOT EXISTS size_violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            db TEXT,
            table_name TEXT,
            size_mb REAL,
            threshold REAL,
            timestamp TEXT
        );
    """,
    "dashboard_alerts": """
        CREATE TABLE IF NOT EXISTS dashboard_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            db TEXT,
            table_name TEXT,
            size_mb REAL,
            threshold REAL,
            timestamp TEXT
        );
    """,
    "cross_link_events": """
        CREATE TABLE IF NOT EXISTS cross_link_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            linked_path TEXT NOT NULL,
            timestamp TEXT NOT NULL
        );
    """,
    "cross_link_suggestions": """
        CREATE TABLE IF NOT EXISTS cross_link_suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            suggested_link TEXT NOT NULL,
            score REAL,
            timestamp TEXT NOT NULL
        );
    """,
    "cross_link_recommendations": """
        CREATE TABLE IF NOT EXISTS cross_link_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            template_id INTEGER,
            score REAL,
            valid INTEGER,
            timestamp TEXT NOT NULL
        );
    """,
    "cross_link_summary": """
        CREATE TABLE IF NOT EXISTS cross_link_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actions INTEGER,
            links INTEGER,
            summary_path TEXT,
            timestamp TEXT NOT NULL
        );
    """,
    "doc_analysis": """
        CREATE TABLE IF NOT EXISTS doc_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            db TEXT,
            level TEXT,
            module TEXT,
            gaps INTEGER,
            before INTEGER,
            after INTEGER,
            removed_backups INTEGER,
            removed_duplicates INTEGER,
            placeholders INTEGER,
            row_count INTEGER,
            table_name TEXT,
            report TEXT,
            rollback TEXT,
            rollback_restored INTEGER,
            ts TEXT,
            timestamp TEXT
        );
    """,
    "workflow_events": """
        CREATE TABLE IF NOT EXISTS workflow_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            level TEXT,
            module TEXT,
            template_count INTEGER,
            cluster_count INTEGER,
            avg_score REAL,
            duration REAL,
            timestamp TEXT
        );
    """,
    "correction_summaries": """
        CREATE TABLE IF NOT EXISTS correction_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            count INTEGER,
            timestamp TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_correction_summaries_timestamp
            ON correction_summaries(timestamp);
    """,
    "rollback_failures": """
        CREATE TABLE IF NOT EXISTS rollback_failures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            module TEXT,
            level TEXT,
            target TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_rollback_failures_timestamp
            ON rollback_failures(timestamp);
    """,
}


def _can_create_analytics_db(db_path: Path = DEFAULT_ANALYTICS_DB) -> bool:
    """
    Test if analytics.db could be created (checks permissions, parent dir, anti-recursion).
    Does NOT actually create the database.
    """
    parent = db_path.resolve().parent
    if str(parent).replace("\\", "/").endswith("/databases"):
        # Passes anti-recursion check (not workspace root or C:\Temp)
        if not parent.exists():
            # Simulate: would attempt to create parent dir
            return os.access(parent.parent, os.W_OK)
        else:
            return os.access(parent, os.W_OK)
    return False


def _resolve_test_mode(test_mode: bool) -> bool:
    """Return effective test mode respecting ``GH_COPILOT_TEST_MODE``."""
    env = os.getenv("GH_COPILOT_TEST_MODE")
    if env is not None:
        return env == "1"
    return test_mode


def ensure_tables(
    db_path: Path,
    tables: Iterable[str],
    *,
    test_mode: bool = False,
) -> None:
    """Ensure the specified tables exist in ``db_path``.

    When ``test_mode`` is ``True`` the function simulates table creation using
    :func:`_log_event` and performs no writes.
    """
    test_mode = _resolve_test_mode(test_mode)

    for table in tables:
        schema = TABLE_SCHEMAS.get(table)
        if not schema:
            continue
        if test_mode:
            logging.getLogger(__name__).info("Simulating table creation: %s in %s", table, db_path)
            continue
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with _log_lock, sqlite3.connect(db_path) as conn:
            conn.executescript(schema)
            conn.commit()


def insert_event(
    event: Dict[str, Any],
    table: str,
    *,
    db_path: Path = DEFAULT_ANALYTICS_DB,
    test_mode: bool = False,
) -> int:
    """Insert ``event`` into the specified table and return the new row id."""
    test_mode = _resolve_test_mode(test_mode)

    ensure_tables(db_path, [table], test_mode=test_mode)
    if test_mode:
        logging.getLogger(__name__).debug("Simulated insert into %s: %s", table, event)
        return -1
    db_path.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(3):
        try:
            with _log_lock, sqlite3.connect(db_path, timeout=30) as conn:
                # Only insert columns that actually exist in the destination table to
                # avoid ``sqlite3.OperationalError`` when the payload contains extra
                # metadata.
                existing_cols = {
                    row[1]
                    for row in conn.execute(f"PRAGMA table_info({table})")
                }
                filtered = {k: v for k, v in event.items() if k in existing_cols}
                if not filtered:
                    logging.getLogger(__name__).debug(
                        "Skipping insert into %s; no matching columns", table
                    )
                    return -1
                columns = ", ".join(filtered.keys())
                placeholders = ", ".join("?" for _ in filtered)
                cur = conn.execute(
                    f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
                    tuple(filtered.values()),
                )
                conn.commit()
                return int(cur.lastrowid)
        except sqlite3.OperationalError as exc:
            if "locked" in str(exc).lower():
                time.sleep(0.1)
                continue
            raise
    raise sqlite3.OperationalError("database is locked")


def _log_event(
    event: Dict[str, Any],
    *,
    table: str = DEFAULT_LOG_TABLE,
    db_path: Path = DEFAULT_ANALYTICS_DB,
    fallback_file: Optional[Path] = None,
    echo: bool = False,
    level: int = logging.INFO,
    test_mode: bool = False,
) -> bool:
    """Log a structured event in a consistent format.

    Parameters
    ----------
    event:
        Dictionary describing the event to record.
    table:
        Destination table name within the analytics database.
    db_path:
        Path to the analytics database file (simulated).
    fallback_file:
        Optional path for writing events if the database is unavailable.
    echo:
        If ``True`` the formatted log line is echoed to the console.
    level:
        Logging level used for the echo output.
    test_mode:
        Override for enabling/disabling database writes. If
        ``GH_COPILOT_TEST_MODE`` is set it takes precedence.

    Returns
    -------
    bool
        ``True`` when the analytics database could be created at ``db_path``.
    """
    test_mode = _resolve_test_mode(test_mode)

    payload = dict(event)
    payload.setdefault("timestamp", datetime.utcnow().isoformat())
    payload.setdefault("module", payload.get("module", __name__))
    payload.setdefault("level", logging.getLevelName(level))

    test_result = _can_create_analytics_db(db_path)
    start_ts = time.time()
    row_id = -1
    with tqdm(total=1, desc="log", unit="evt", leave=False) as bar:
        if test_result:
            ensure_tables(db_path, [table], test_mode=test_mode)
            row_id = insert_event(
                payload, table, db_path=db_path, test_mode=test_mode
            )
            bar.set_postfix_str(
                "simulated" if test_mode or row_id == -1 else "written"
            )
        else:
            tqdm.write(f"[FAIL] analytics.db could NOT be created at: {db_path}")
            if fallback_file:
                _setup_file_logger(fallback_file, level=level).info(json.dumps(payload))
            bar.set_postfix_str("ERROR")
        bar.update(1)
    duration = time.time() - start_ts
    logger = logging.getLogger(__name__)
    status = "SIMULATED" if test_mode or row_id == -1 else "LOGGED"
    prefix = "Simulated " if status == "SIMULATED" else ""
    logger.info(
        "%sanalytics.db log event: %s | %.2fs | allowed: %s",
        prefix,
        json.dumps(payload),
        duration,
        test_result,
    )
    if echo:
        print(
            f"[LOG][{payload['timestamp']}][{table}][{status}] {json.dumps(payload)}",
            file=sys.stderr if level >= logging.ERROR else sys.stdout,
        )
    return test_result


def _setup_file_logger(
    log_file: Path, level: int = logging.INFO, fmt: str = "%(asctime)s %(levelname)s %(message)s"
) -> logging.Logger:
    """
    Set up a file logger.
    Returns a logger instance.
    """
    logger = logging.getLogger(str(log_file))
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def _log_audit_event(
    description: str,
    details: Optional[Dict[str, Any]] = None,
    level: int = logging.INFO,
    db_path: Path = DEFAULT_ANALYTICS_DB,
    table: str = "audit_log",
    echo: bool = False,
    test_mode: bool = False,
) -> bool:
    """Record an audit event in the analytics log.

    Parameters
    ----------
    description:
        Brief text describing the audit entry.
    details:
        Optional dictionary containing extra information.
    level:
        Logging level for echo output.
    db_path:
        Path to the analytics database file (simulated).
    table:
        Table name within the analytics database.
    echo:
        If ``True`` the formatted log line is echoed to the console.
    test_mode:
        When ``True`` the function only simulates the operation and returns the
        result of :func:`_log_event`.

    Returns
    -------
    bool
        ``True`` when the analytics database could be created at ``db_path``.
    """
    test_mode = _resolve_test_mode(test_mode)

    event = {
        "description": description,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
    }
    return _log_event(
        event,
        table=table,
        db_path=db_path,
        echo=echo,
        level=level,
        test_mode=test_mode,
    )


def _log_plain(
    msg: str,
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    echo: bool = True,
) -> None:
    """
    Simulate logging a plain text message (optionally to file), always with timestamp.
    """
    timestamp = datetime.utcnow().isoformat()
    line = f"{timestamp} [{logging.getLevelName(level)}] {msg} [SIMULATED]"
    if log_file:
        tqdm.write(f"[TEST] Would write to log file: {log_file}")
    if echo:
        print(line, file=sys.stderr if level >= logging.ERROR else sys.stdout)


def log_message(module: str, message: str, *, level: int = logging.INFO) -> None:
    """Emit a standardized log message.

    Parameters
    ----------
    module:
        Name of the calling module.
    message:
        Human readable log message.
    level:
        Logging severity level.

    Expected Outcome
    ----------------
    A timestamped log line is printed using :func:`_log_plain` with the module
    name prefixed to the message.
    """

    formatted = f"[{module}] {message}"
    _log_plain(formatted, level=level)


def log_event(event: Dict[str, Any], *, table: str = DEFAULT_LOG_TABLE, db_path: Path = DEFAULT_ANALYTICS_DB) -> None:
    """Write an event directly to analytics.db."""
    ensure_tables(db_path, [table], test_mode=False)
    event = dict(event)
    event.setdefault("timestamp", datetime.utcnow().isoformat())
    insert_event(event, table, db_path=db_path, test_mode=False)


def send_dashboard_alert(
    event: Dict[str, Any], *, table: str = "dashboard_alerts", db_path: Path = DEFAULT_ANALYTICS_DB
) -> None:
    """Send an alert event to the web dashboard if enabled."""
    if os.getenv("WEB_DASHBOARD_ENABLED") != "1":
        return
    log_event(event, table=table, db_path=db_path)


def stream_events(
    table: str = DEFAULT_LOG_TABLE,
    *,
    db_path: Path = DEFAULT_ANALYTICS_DB,
):
    """Yield events formatted for Server-Sent Events."""
    if not db_path.exists():
        return
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        for row in conn.execute(f"SELECT * FROM {table} ORDER BY id ASC"):
            rec = dict(row)
            category = rec.get("category") or table
            yield f"event: {category}\ndata: {json.dumps(rec)}\n\n"


def log_stream(
    table: str = DEFAULT_LOG_TABLE,
    *,
    db_path: Path = DEFAULT_ANALYTICS_DB,
    poll_interval: float = 1.0,
) -> Iterable[str]:
    """Continuously yield events as Server-Sent Event strings."""
    last_id = 0
    while True:
        if not db_path.exists():
            time.sleep(poll_interval)
            continue
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                f"SELECT * FROM {table} WHERE id > ? ORDER BY id ASC",
                (last_id,),
            )
            for row in rows:
                last_id = row["id"]
                rec = dict(row)
                category = rec.get("category") or table
                yield f"event: {category}\ndata: {json.dumps(rec)}\n\n"
        time.sleep(poll_interval)


def sse_event_stream(
    table: str = DEFAULT_LOG_TABLE,
    *,
    db_path: Path = DEFAULT_ANALYTICS_DB,
    poll_interval: float = 1.0,
) -> Iterable[str]:
    """Return a generator yielding Server-Sent Event strings.

    This helper wraps :func:`log_stream` so the result can be passed
    directly to :class:`flask.Response` for SSE endpoints.
    """

    return log_stream(table, db_path=db_path, poll_interval=poll_interval)


def _list_events(
    table: str = DEFAULT_LOG_TABLE,
    db_path: Path = DEFAULT_ANALYTICS_DB,
    limit: int = 100,
    order: str = "DESC",
    *,
    test_mode: bool = False,
) -> list:
    """Return recent events from ``table`` respecting test mode."""
    test_mode = _resolve_test_mode(test_mode)
    if test_mode or not db_path.exists():
        tqdm.write(f"[TEST] Listing would query {table} in {db_path} (simulated, no DB access)")
        return []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            f"SELECT * FROM {table} ORDER BY id {order} LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def _clear_log(
    table: str = DEFAULT_LOG_TABLE,
    db_path: Path = DEFAULT_ANALYTICS_DB,
    *,
    test_mode: bool = False,
) -> bool:
    """Remove all rows from ``table`` respecting test mode."""
    test_mode = _resolve_test_mode(test_mode)
    if test_mode:
        tqdm.write(f"[TEST] Clearing would delete all from {table} in {db_path} (simulated, no DB access)")
        return True
    if not db_path.exists():
        return False
    with sqlite3.connect(db_path) as conn:
        conn.execute(f"DELETE FROM {table}")
        conn.commit()
    return True


# --------- HUMAN TRIGGER REQUIRED TO CREATE analytics.db ----------
#
# To actually create the analytics.db and required tables, run:
#
#   sqlite3 databases/analytics.db < databases/migrations/add_code_audit_log.sql
#   sqlite3 databases/analytics.db < databases/migrations/add_correction_history.sql
#
#   # To verify:
#   sqlite3 databases/analytics.db ".schema code_audit_log"
#   sqlite3 databases/analytics.db ".schema correction_history"
#
# See ``docs/ANALYTICS_DB_TEST_PROTOCOL.md`` for full instructions on manual database creation.
#
# ---------------------------------------------------------------

__all__ = [
    "ensure_tables",
    "insert_event",
    "log_message",
    "log_event",
    "send_dashboard_alert",
    "stream_events",
    "log_stream",
    "sse_event_stream",
    "start_websocket_broadcast",
    "_log_event",
    "_log_audit_event",
]


def start_websocket_broadcast(
    host: str = "localhost",
    port: int = 8765,
    *,
    table: str = DEFAULT_LOG_TABLE,
    db_path: Path = DEFAULT_ANALYTICS_DB,
    poll_interval: float = 1.0,
) -> None:
    """Start a simple WebSocket server broadcasting log events.

    The server runs only when ``LOG_WEBSOCKET_ENABLED`` is ``"1"``.
    Clients receive the same payload as :func:`sse_event_stream`.
    """

    if os.environ.get("LOG_WEBSOCKET_ENABLED") != "1":
        return

    try:
        import websockets
    except ImportError:  # pragma: no cover - optional dependency
        logging.getLogger(__name__).warning("websockets package not available - skipping broadcast")
        return

    import asyncio

    clients: set = set()

    async def _producer() -> None:
        for event in log_stream(table, db_path=db_path, poll_interval=poll_interval):
            for ws in list(clients):
                try:
                    await ws.send(event)
                except websockets.ConnectionClosed:
                    clients.discard(ws)

    async def _handler(websocket: websockets.WebSocketServerProtocol) -> None:
        clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            clients.discard(websocket)

    async def _main() -> None:
        server = await websockets.serve(_handler, host, port)
        try:
            await _producer()
        finally:
            server.close()
            await server.wait_closed()

    asyncio.run(_main())
