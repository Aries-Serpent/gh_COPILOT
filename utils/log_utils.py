import json
import logging
import os
import sqlite3
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Default analytics DB path (can be overridden by environment variable)
DEFAULT_ANALYTICS_DB = Path(os.environ.get("ANALYTICS_DB", "analytics.db"))
DEFAULT_LOG_TABLE = "event_log"
_log_lock = threading.Lock()

def _log_event(
    event: Dict[str, Any],
    *,
    table: str = DEFAULT_LOG_TABLE,
    db_path: Path = DEFAULT_ANALYTICS_DB,
    fallback_file: Optional[Path] = None,
    echo: bool = False,
    level: int = logging.INFO,
) -> bool:
    """
    Log a structured event to the analytics SQLite DB (or fallback file).
    - event: dict of event attributes to log (must be JSON-serializable)
    - table: table to log to (default: event_log)
    - db_path: SQLite DB file (default: analytics.db)
    - fallback_file: if provided and DB fails, append JSON log to this file
    - echo: print the log to stdout/stderr as well
    - level: logging level for echo (default: INFO)
    Returns True if the log succeeded, False if it failed everywhere.
    """
    payload = dict(event)
    if "timestamp" not in payload:
        payload["timestamp"] = datetime.utcnow().isoformat()

    try:
        _log_lock.acquire()
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute(
                f"""CREATE TABLE IF NOT EXISTS {table}
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 timestamp TEXT,
                 event_json TEXT)"""
            )
            conn.execute(
                f"""INSERT INTO {table} (timestamp, event_json) VALUES (?, ?)""",
                (payload["timestamp"], json.dumps(payload)),
            )
            conn.commit()
        if echo:
            print(f"[LOG][{payload['timestamp']}][{table}] {json.dumps(payload)}", file=sys.stderr if level >= logging.ERROR else sys.stdout)
        return True
    except Exception as db_exc:
        if fallback_file:
            try:
                with open(fallback_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(payload) + "\n")
                if echo:
                    print(f"[LOG-FALLBACK][{payload['timestamp']}][{table}] {json.dumps(payload)}", file=sys.stderr if level >= logging.ERROR else sys.stdout)
                return True
            except Exception as file_exc:
                if echo:
                    print(f"[LOG-FAIL][{payload['timestamp']}][{table}] DB: {db_exc} | FILE: {file_exc}", file=sys.stderr)
                return False
        else:
            if echo:
                print(f"[LOG-FAIL][{payload['timestamp']}][{table}] DB: {db_exc}", file=sys.stderr)
            return False
    finally:
        _log_lock.release()

def _setup_file_logger(
    log_file: Path,
    level: int = logging.INFO,
    fmt: str = "%(asctime)s %(levelname)s %(message)s"
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
) -> bool:
    """
    Log an audit event to analytics DB/audit_log table.
    """
    event = {
        "description": description,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
    }
    return _log_event(event, table=table, db_path=db_path, echo=echo, level=level)

def _log_plain(
    msg: str,
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    echo: bool = True,
) -> None:
    """
    Log a plain text message (optionally to file), always with timestamp.
    """
    timestamp = datetime.utcnow().isoformat()
    line = f"{timestamp} [{logging.getLevelName(level)}] {msg}"
    if log_file:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    if echo:
        print(line, file=sys.stderr if level >= logging.ERROR else sys.stdout)

def _list_events(
    table: str = DEFAULT_LOG_TABLE,
    db_path: Path = DEFAULT_ANALYTICS_DB,
    limit: int = 100,
    order: str = "DESC"
) -> list:
    """
    List the most recent events from the log table.
    """
    try:
        db_path = Path(db_path)
        with sqlite3.connect(str(db_path)) as conn:
            rows = conn.execute(
                f"SELECT timestamp, event_json FROM {table} ORDER BY id {order} LIMIT ?", (limit,)
            ).fetchall()
            events = [(ts, json.loads(ej)) for ts, ej in rows]
            return events
    except Exception as exc:
        print(f"[LOG][ERROR][LIST] Failed to retrieve events: {exc}", file=sys.stderr)
        return []

def _clear_log(
    table: str = DEFAULT_LOG_TABLE,
    db_path: Path = DEFAULT_ANALYTICS_DB,
) -> bool:
    """
    Clear all events from the log table.
    """
    try:
        db_path = Path(db_path)
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute(f"DELETE FROM {table}")
            conn.commit()
        return True
    except Exception as exc:
        print(f"[LOG][ERROR][CLEAR] Failed to clear log: {exc}", file=sys.stderr)
        return False
