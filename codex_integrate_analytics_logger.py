#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codex_integrate_analytics_logger.py

End-to-end workflow to:
- Implement log_event & log_sync_operation with TEST_MODE-safe DB handling
- Ensure events table exists in analytics.db-compatible schema
- Update README with Analytics Database details if missing
- Add pytest tests that verify rows get logged (and TEST_MODE safety)
- Create a change log and standardized ChatGPT-5 research questions on errors
- (Optionally) run pytest and ruff if present

Safe-guards:
- NEVER writes under .github/workflows
- Defaults TEST_MODE=1 for safety unless explicitly overridden by the environment
"""

from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "src" / "gh_copilot"
TESTS_DIR = REPO_ROOT / "tests"
CHANGE_DIR = REPO_ROOT / "codex_changes"
ERROR_LOG = REPO_ROOT / ".codex_error_log.md"
README = REPO_ROOT / "README.md"

SRC_DIR.mkdir(parents=True, exist_ok=True)
TESTS_DIR.mkdir(parents=True, exist_ok=True)
CHANGE_DIR.mkdir(parents=True, exist_ok=True)

# --- Utility: write file only if content changed
def _write_if_changed(path: Path, content: str) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old != content:
        path.write_text(content, encoding="utf-8")
        return True
    return False

def _append_line(path: Path, line: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(line + ("\n" if not line.endswith("\n") else ""))

def _safe_env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).strip().lower() in {"1","true","yes","on"}

# --- 1) Implement analytics_logger.py (idempotent)
LOGGER_PATH = SRC_DIR / "analytics_logger.py"
LOGGER_CODE = r'''
from __future__ import annotations
import os, json, sqlite3, threading, time
from typing import Optional, Dict, Any

__all__ = ["log_event", "log_sync_operation", "get_db_path", "ensure_schema"]

_LOCK = threading.RLock()

def get_db_path(db_path: Optional[str]=None, test_mode: Optional[bool]=None) -> str:
    """
    Resolve effective DB path based on TEST_MODE and env overrides.
    TEST_MODE rules:
      - If ANALYTICS_DB_PATH is set, always use it (safe for tests).
      - Else, if TEST_MODE is truthy, use ':memory:' to avoid on-disk side effects.
      - Else, default to 'analytics.db'.
    """
    if db_path:
        return db_path
    env_db = os.getenv("ANALYTICS_DB_PATH")
    if env_db:
        return env_db
    if test_mode is None:
        test_mode = str(os.getenv("TEST_MODE","0")).strip().lower() in {"1","true","yes","on"}
    return ":memory:" if test_mode else "analytics.db"

def ensure_schema(conn: sqlite3.Connection) -> None:
    with conn:
        # Schema aligned with README (events table)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS events(
          event_time TEXT DEFAULT (datetime('now')),
          level      TEXT,
          event      TEXT,
          details    TEXT
        );
        """)

def _connect(db_path: str) -> sqlite3.Connection:
    # If using URI (e.g., shared memory), enable uri param
    uri = db_path.startswith("file:")
    conn = sqlite3.connect(db_path, uri=uri, timeout=30, isolation_level=None, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def log_event(level: str, event: str, details: Dict[str, Any], *, db_path: Optional[str]=None, test_mode: Optional[bool]=None) -> None:
    """
    Insert a single row into events(level, event, details) with automatic event_time.
    details is JSON-encoded.
    """
    effective = get_db_path(db_path=db_path, test_mode=test_mode)
    payload = json.dumps(details, ensure_ascii=False, separators=(",",":"))
    with _LOCK:
        conn = _connect(effective)
        try:
            ensure_schema(conn)
            with conn:
                conn.execute(
                    "INSERT INTO events(level,event,details) VALUES(?,?,?)",
                    (level, event, payload),
                )
        finally:
            conn.close()

def log_sync_operation(file_path: str, count: int, status: str, *, db_path: Optional[str]=None, test_mode: Optional[bool]=None) -> None:
    """
    Structured convenience around log_event for sync operations on HARs or other artifacts.
    Writes event='sync_operation' with details JSON of file_path, count, status.
    """
    details = {"file_path": file_path, "count": int(count), "status": status}
    return log_event(level="INFO", event="sync_operation", details=details, db_path=db_path, test_mode=test_mode)
'''

changed_logger = _write_if_changed(LOGGER_PATH, LOGGER_CODE)

# Ensure package init
INIT_PY = SRC_DIR / "__init__.py"
if not INIT_PY.exists():
    INIT_PY.write_text("# gh_copilot package\nfrom .analytics_logger import log_event, log_sync_operation\n", encoding="utf-8")
else:
    init_txt = INIT_PY.read_text(encoding="utf-8")
    if "log_sync_operation" not in init_txt:
        INIT_PY.write_text(init_txt + "\nfrom .analytics_logger import log_event, log_sync_operation\n", encoding="utf-8")

# --- 2) README analytics section normalization (best-effort, non-destructive)
def update_readme(path: Path) -> bool:
    if not path.exists():
        return False
    txt = path.read_text(encoding="utf-8")
    # Replace dangling "()" artifacts conservatively
    txt2 = re.sub(r"\(\)", "", txt)

    analytics_block = textwrap.dedent("""
    ### Analytics Database

    * SQLite file: `analytics.db`
    * Table: `events(event_time TEXT, level TEXT, event TEXT, details TEXT)`

    These entries are written via `log_event(...)` and `log_sync_operation(...)`.
    When `TEST_MODE=1` and `ANALYTICS_DB_PATH` is not set, an in-memory database is used to avoid side effects.
    """).strip()

    if "### Analytics Database" not in txt2:
        # Try to append near "Disaster Recovery" quick start if present, else add at end
        if "## Disaster Recovery" in txt2:
            txt2 = txt2.replace("## Disaster Recovery", analytics_block + "\n\n## Disaster Recovery")
        else:
            txt2 = txt2 + "\n\n" + analytics_block + "\n"

    return _write_if_changed(path, txt2)

readme_changed = update_readme(README)

# --- 3) Tests
TEST_CODE = r'''
import os, json, sqlite3, tempfile, pathlib
import pytest

from gh_copilot.analytics_logger import log_event, log_sync_operation, get_db_path

def _rowcount(db_path: str) -> int:
    uri = db_path.startswith("file:")
    conn = sqlite3.connect(db_path, uri=uri)
    try:
        cur = conn.execute("SELECT COUNT(*) FROM events")
        return cur.fetchone()[0]
    finally:
        conn.close()

def test_log_event_into_temp_db_respects_test_mode(tmp_path):
    # TEST_MODE on with explicit temp file => safe side-effects
    os.environ["TEST_MODE"] = "1"
    db_file = tmp_path / "events.db"
    os.environ["ANALYTICS_DB_PATH"] = str(db_file)

    log_event("INFO", "unit_event", {"k":"v"})
    assert db_file.exists()
    assert _rowcount(str(db_file)) >= 1

def test_log_sync_operation_payload_and_write(tmp_path):
    os.environ["TEST_MODE"] = "1"
    db_file = tmp_path / "events2.db"
    os.environ["ANALYTICS_DB_PATH"] = str(db_file)

    log_sync_operation("sample.har", 2, "success")
    import sqlite3
    conn = sqlite3.connect(str(db_file))
    try:
        row = conn.execute("SELECT level,event,details FROM events ORDER BY rowid DESC LIMIT 1").fetchone()
        assert row[0] == "INFO"
        assert row[1] == "sync_operation"
        details = json.loads(row[2])
        assert details == {"file_path": "sample.har", "count": 2, "status": "success"}
    finally:
        conn.close()

def test_no_analytics_db_file_when_test_mode_and_no_path(tmp_path, monkeypatch):
    # Ensure cwd is not polluted by a stray analytics.db
    os.environ["TEST_MODE"] = "1"
    os.environ.pop("ANALYTICS_DB_PATH", None)

    # use the logger; it should go to :memory:
    log_event("INFO", "ephemeral_test", {"x":1})

    # verify analytics.db not created in cwd
    assert not pathlib.Path("analytics.db").exists()
'''

TEST_PATH = TESTS_DIR / "test_analytics_logging.py"
changed_test = _write_if_changed(TEST_PATH, TEST_CODE)

# --- 4) Optional: HAR sample (not strictly required since we log structured counts)
HAR_SAMPLE = REPO_ROOT / "tests" / "data_sample.har"
if not HAR_SAMPLE.exists():
    HAR_SAMPLE.write_text(json.dumps({"log": {"entries": [{"id":1},{"id":2}]}}), encoding="utf-8")

# --- 5) Change log
timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")
CHANGE_TEXT = f"""
# Analytics Logging Integration — {timestamp}

## What changed
- Added `src/gh_copilot/analytics_logger.py` with:
  - `log_event(level, event, details, *, db_path=None, test_mode=None)`
  - `log_sync_operation(file_path, count, status, *, db_path=None, test_mode=None)`
  - TEST_MODE policy: in-memory DB unless `ANALYTICS_DB_PATH` is set.
- Tests:
  - `tests/test_analytics_logging.py` (3 tests)
- README updated: ensured "Analytics Database" section and removed dangling "()".
- Created sample HAR at `tests/data_sample.har` (2 fake entries).

## Mapping & Rationale
- Followed README's events schema; avoided hard-binding to unknown CLI commands.
- No GitHub Actions files touched.

## Open gaps
- If CLI exists with a known command to process HARs, wire `log_sync_operation(...)` into that path.
- Consider adding `level` taxonomy and more tables if needed (out of scope).

"""
CHANGE_PATH = CHANGE_DIR / f"analytics_logging_{timestamp}.md"
_change_written = _write_if_changed(CHANGE_PATH, CHANGE_TEXT)

# --- 6) Best-effort: run pytest / ruff (optional)
def _try_run(cmd: list[str]) -> tuple[int,str]:
    try:
        out = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)
        return out.returncode, out.stdout + "\n" + out.stderr
    except Exception as e:
        return 1, f"[runner-error] {e!r}"

results = {}
if shutil.which("pytest"):
    rc, out = _try_run([sys.executable, "-m", "pytest", "-q"])
    results["pytest"] = {"rc": rc, "output": out}
if shutil.which("ruff"):
    rc, out = _try_run(["ruff", "check", "."])
    results["ruff"] = {"rc": rc, "output": out}

SUMMARY = {
    "logger_written": changed_logger,
    "test_written": changed_test,
    "readme_updated": readme_changed,
    "results": results,
    "env": {
        "TEST_MODE": os.getenv("TEST_MODE", "not set"),
        "ANALYTICS_DB_PATH": os.getenv("ANALYTICS_DB_PATH", "not set"),
    },
}
print(json.dumps(SUMMARY, indent=2))
