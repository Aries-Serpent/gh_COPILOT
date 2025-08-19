# Auto-generated analytics logger
from __future__ import annotations
import json
import os
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

__all__ = ["log_analytics_event", "get_run_id"]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_run_id() -> str:
    return os.environ.get("GH_COPILOT_RUN_ID") or str(uuid.uuid4())


def log_analytics_event(
    db_path: str | os.PathLike,
    *,
    level: str,
    step: str,
    phase: str,
    event: str,
    details: dict | None = None,
    run_id: Optional[str] = None,
    error: str | None = None,
    table: str = "events",
    fallback_file: str | os.PathLike | None = None,
) -> bool:
    """Insert an analytics event, avoiding schema mutations.

    Attempts to insert into ``table`` without creating or migrating schemas.
    On failure (e.g., missing table), a JSONL fallback file is written and
    ``False`` is returned.
    """
    run_id = run_id or get_run_id()
    payload = {
        "event_time": _now_iso(),
        "level": level,
        "event": event,
        "details": json.dumps(
            {
                "phase": phase,
                "step": step,
                "run_id": run_id,
                "meta": details or {},
                "error": error,
            },
            ensure_ascii=False,
        ),
    }
    try:
        conn = sqlite3.connect(str(db_path))
        try:
            with conn:
                conn.execute(
                    f"INSERT INTO {table}(event_time, level, event, details) VALUES (:event_time, :level, :event, :details)",
                    payload,
                )
        finally:
            conn.close()
        return True
    except Exception as e:  # pragma: no cover - fallback path
        record = {
            "fallback_time": _now_iso(),
            "reason": f"{type(e).__name__}: {e}",
            "attempt": payload,
        }
        if fallback_file:
            Path(fallback_file).parent.mkdir(parents=True, exist_ok=True)
            with open(fallback_file, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return False
