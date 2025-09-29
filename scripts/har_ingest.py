#!/usr/bin/env python
from __future__ import annotations

"""HAR ingestion pipeline using gh_copilot.automation primitives.

Phases (StepCtx):
1) Validate file path (exists, readable, basic extension/size checks)
2) JSON schema check (ensure minimal HAR structure: log.entries[])
3) Parse entries (normalize selected fields)
4) Write to SQLite (APPLY only; DRY_RUN verifies schema only)
5) Emit metrics (append NDJSON event)

Environment:
- DRY_RUN ("1" default): simulate writes; do not touch the database
- APPLY ("1" when applying): enables guardrails to protect repo invariants

Usage:
    python scripts/har_ingest.py path/to/file.har [--db databases/har_ingest.db]
"""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


# Ensure package imports when invoked directly from repo root
sys.path.insert(0, os.getcwd())

from gh_copilot.automation.core import StepCtx, run_phases  # type: ignore
from gh_copilot.automation.guardrails import (  # type: ignore
    guard_no_github_actions,
    guard_no_recursive_backups,
    validate_no_forbidden_paths,
)
from gh_copilot.automation.logging import append_ndjson  # type: ignore


@dataclass
class IngestContext:
    src_path: Path
    db_path: Path
    dry_run: bool
    ndjson_path: Path
    repo_root: Path
    # Filled during phases
    raw_har: Optional[Dict[str, Any]] = None
    total_entries: int = 0
    normalized: List[Dict[str, Any]] = None  # type: ignore[assignment]


def _git_root_fallback() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        return Path(out) if out else Path.cwd()
    except Exception:
        return Path.cwd()


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate_file(ctx: IngestContext) -> None:
    p = ctx.src_path
    validate_no_forbidden_paths(str(p))
    if not p.exists():
        raise FileNotFoundError(str(p))
    if not p.is_file():
        raise ValueError(f"Not a file: {p}")
    if p.suffix.lower() not in {".har", ".json", ""}:
        # Permit .json or no extension; warn but continue
        pass
    if p.stat().st_size <= 0:
        raise ValueError("Empty file")


def _load_and_check_schema(ctx: IngestContext) -> None:
    text = ctx.src_path.read_text(encoding="utf-8", errors="replace")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
    if not isinstance(payload, dict) or "log" not in payload or not isinstance(payload["log"], dict):
        raise ValueError("HAR must contain top-level 'log' object")
    log = payload["log"]
    entries = log.get("entries")
    if not isinstance(entries, list):
        raise ValueError("HAR 'log.entries' must be a list")
    ctx.raw_har = payload
    ctx.total_entries = len(entries)


def _normalize_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    log_time = entry.get("startedDateTime") or ""
    req = entry.get("request", {}) if isinstance(entry.get("request"), dict) else {}
    res = entry.get("response", {}) if isinstance(entry.get("response"), dict) else {}
    timings = entry.get("timings", {}) if isinstance(entry.get("timings"), dict) else {}

    method = str(req.get("method") or "")
    url = str(req.get("url") or "")
    status = int(res.get("status") or 0)
    status_text = str(res.get("statusText") or "")
    mime_type = ""
    content = res.get("content")
    if isinstance(content, dict):
        mime_type = str(content.get("mimeType") or "")

    def _ms(v: Any) -> float:
        try:
            x = float(v)
            return 0.0 if x < 0 else x
        except Exception:
            return 0.0

    wait_ms = _ms(timings.get("wait"))
    blocked_ms = _ms(timings.get("blocked"))
    dns_ms = _ms(timings.get("dns"))
    connect_ms = _ms(timings.get("connect"))
    ssl_ms = _ms(timings.get("ssl"))
    send_ms = _ms(timings.get("send"))
    receive_ms = _ms(timings.get("receive"))
    total_ms = sum((wait_ms, blocked_ms, dns_ms, connect_ms, ssl_ms, send_ms, receive_ms))

    host = ""
    path = ""
    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        host = parsed.netloc
        path = parsed.path
    except Exception:
        pass

    return {
        "started_at": log_time,
        "method": method,
        "url": url,
        "host": host,
        "path": path,
        "status": status,
        "status_text": status_text,
        "mime_type": mime_type,
        "wait_ms": wait_ms,
        "blocked_ms": blocked_ms,
        "dns_ms": dns_ms,
        "connect_ms": connect_ms,
        "ssl_ms": ssl_ms,
        "send_ms": send_ms,
        "receive_ms": receive_ms,
        "total_ms": total_ms,
    }


def _parse_entries(ctx: IngestContext) -> None:
    assert ctx.raw_har is not None
    entries = ctx.raw_har.get("log", {}).get("entries", [])
    normalized: List[Dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        normalized.append(_normalize_entry(e))
    ctx.normalized = normalized


def _write_db(ctx: IngestContext) -> None:
    # Guardrails before side effects
    guard_no_recursive_backups(str(ctx.repo_root))
    guard_no_github_actions(str(ctx.repo_root))
    validate_no_forbidden_paths(str(ctx.db_path))

    if ctx.dry_run:
        return
    ctx.db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(ctx.db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS har_entries (
              id INTEGER PRIMARY KEY,
              started_at TEXT,
              method TEXT,
              url TEXT,
              host TEXT,
              path TEXT,
              status INTEGER,
              status_text TEXT,
              mime_type TEXT,
              wait_ms REAL,
              blocked_ms REAL,
              dns_ms REAL,
              connect_ms REAL,
              ssl_ms REAL,
              send_ms REAL,
              receive_ms REAL,
              total_ms REAL
            )
            """
        )
        rows = [
            (
                r["started_at"],
                r["method"],
                r["url"],
                r["host"],
                r["path"],
                r["status"],
                r["status_text"],
                r["mime_type"],
                r["wait_ms"],
                r["blocked_ms"],
                r["dns_ms"],
                r["connect_ms"],
                r["ssl_ms"],
                r["send_ms"],
                r["receive_ms"],
                r["total_ms"],
            )
            for r in ctx.normalized
        ]
        cur.executemany(
            """
            INSERT INTO har_entries (
              started_at, method, url, host, path, status, status_text, mime_type,
              wait_ms, blocked_ms, dns_ms, connect_ms, ssl_ms, send_ms, receive_ms, total_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
    finally:
        conn.close()


def _emit_metrics(ctx: IngestContext) -> None:
    append_ndjson(
        str(ctx.ndjson_path),
        {
            "event": "har_ingest",
            "ts": _iso_now(),
            "file": str(ctx.src_path),
            "total_entries": ctx.total_entries,
            "normalized_count": len(ctx.normalized or []),
            "db_path": str(ctx.db_path),
            "dry_run": ctx.dry_run,
        },
    )


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("har_path", help="Path to a HAR (.har) or JSON file")
    parser.add_argument(
        "--db",
        dest="db_path",
        default=os.path.join("databases", "har_ingest.db"),
        help="SQLite destination (APPLY only)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    dry_run = os.environ.get("DRY_RUN", "1") != "0"
    ndjson_path = Path(".codex") / "action_log.ndjson"
    src_path = Path(args.har_path).resolve()
    db_path = Path(args.db_path)
    repo_root = _git_root_fallback()

    ctx = IngestContext(
        src_path=src_path,
        db_path=db_path,
        dry_run=dry_run,
        ndjson_path=ndjson_path,
        repo_root=repo_root,
        normalized=[],
    )

    phases = [
        StepCtx(name="Validate", desc="Validate HAR path", fn=lambda: _validate_file(ctx)),
        StepCtx(name="Schema", desc="Load + schema check", fn=lambda: _load_and_check_schema(ctx)),
        StepCtx(name="Parse", desc="Normalize entries", fn=lambda: _parse_entries(ctx)),
        StepCtx(name="Persist", desc="Write to SQLite (APPLY only)", fn=lambda dry_run=dry_run: (_write_db(ctx) if not dry_run else None)),
        StepCtx(name="Metrics", desc="Emit NDJSON metrics", fn=lambda: _emit_metrics(ctx)),
    ]

    result = run_phases(phases, dry_run=dry_run)
    print(
        json.dumps(
            {
                "ok": result.ok,
                "phases_completed": result.phases_completed,
                "entries": ctx.total_entries,
                "normalized": len(ctx.normalized or []),
                "db": str(ctx.db_path),
                "dry_run": ctx.dry_run,
            }
        )
    )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

