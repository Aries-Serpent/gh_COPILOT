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
    pages_count: int = 0
    meta_creator: Optional[str] = None
    meta_browser: Optional[str] = None
    normalized: List[Dict[str, Any]] = None  # type: ignore[assignment]
    # Optional outputs
    pages_jsonl_path: Optional[Path] = None
    pages_preview_jsonl_path: Optional[Path] = None


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
    # Optional lightweight validation for pages array
    pages = log.get("pages")
    if pages is not None and not isinstance(pages, list):
        raise ValueError("HAR 'log.pages' must be a list if present")
    ctx.pages_count = len(pages or []) if isinstance(pages, list) else 0

    # Capture minimal creator/browser metadata for optional metrics emission
    creator = log.get("creator")
    if isinstance(creator, dict):
        name = creator.get("name")
        ver = creator.get("version")
        if isinstance(name, str) and name:
            ctx.meta_creator = f"{name}/{ver}" if isinstance(ver, (str, int, float)) else str(name)
    browser = log.get("browser")
    if isinstance(browser, dict):
        name = browser.get("name")
        ver = browser.get("version")
        if isinstance(name, str) and name:
            ctx.meta_browser = f"{name}/{ver}" if isinstance(ver, (str, int, float)) else str(name)
    ctx.raw_har = payload
    ctx.total_entries = len(entries)
    # Strict schema (optional)
    if os.environ.get("HAR_STRICT_SCHEMA", "0") == "1":
        # Enforce presence of creator/browser name+version
        for key in ("creator", "browser"):
            obj = log.get(key)
            if not isinstance(obj, dict):
                raise ValueError(f"HAR strict mode: missing '{key}' object")
            if not obj.get("name"):
                raise ValueError(f"HAR strict mode: '{key}.name' required")
            if "version" not in obj:
                raise ValueError(f"HAR strict mode: '{key}.version' required")


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

    # Optional: redact headers/content fields if present (PII safety)
    # Defaults: NEVER redact; users must set flags explicitly.
    if os.environ.get("HAR_REDACT_HEADERS", "0") == "1":
        # Placeholder for future header redaction when headers are included.
        # Currently, normalization does not extract headers; this block
        # exists to document the control surface and future behavior.
        pass
    if os.environ.get("HAR_REDACT_BODIES", "0") == "1":
        # Placeholder for future body/content redaction when bodies are included.
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


def _extract_headers_and_bodies(entry: Dict[str, Any], *, redact_headers: bool, redact_bodies: bool) -> Dict[str, Any]:
    """Extract request/response headers and bodies from a HAR entry.

    - Returns JSON-serializable dict with keys:
      req_headers_json, res_headers_json (list of {name,value})
      req_body_text (str|None), req_body_mime (str)
      res_body_text (str|None), res_body_mime (str), res_body_encoding (str|None)
    - When redaction flags are enabled, header values and/or body text are replaced
      with the string "[REDACTED]".
    """
    req = entry.get("request", {}) if isinstance(entry.get("request"), dict) else {}
    res = entry.get("response", {}) if isinstance(entry.get("response"), dict) else {}

    def _headers(obj: Any) -> List[Dict[str, str]]:
        hs = obj.get("headers") if isinstance(obj, dict) else None
        if not isinstance(hs, list):
            return []
        out: List[Dict[str, str]] = []
        for item in hs:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "")
            val = item.get("value")
            sval = "" if val is None else str(val)
            if redact_headers:
                sval = "[REDACTED]"
            out.append({"name": name, "value": sval})
        return out

    def _req_body(obj: Any) -> Tuple[Optional[str], str]:
        if not isinstance(obj, dict):
            return None, ""
        pd = obj.get("postData")
        if not isinstance(pd, dict):
            return None, ""
        text = pd.get("text")
        mime = pd.get("mimeType")
        if text is not None and not isinstance(text, str):
            text = str(text)
        if redact_bodies and text is not None:
            text = "[REDACTED]"
        return (text, str(mime or ""))

    def _res_body(obj: Any) -> Tuple[Optional[str], str, Optional[str]]:
        if not isinstance(obj, dict):
            return None, "", None
        content = obj.get("content")
        if not isinstance(content, dict):
            return None, "", None
        text = content.get("text")
        mime = content.get("mimeType")
        enc = content.get("encoding")
        if text is not None and not isinstance(text, str):
            text = str(text)
        if redact_bodies and text is not None:
            text = "[REDACTED]"
        return (text, str(mime or ""), str(enc) if enc is not None else None)

    req_headers = _headers(req)
    res_headers = _headers(res)
    req_text, req_mime = _req_body(req)
    res_text, res_mime, res_enc = _res_body(res)
    return {
        "req_headers_json": req_headers,
        "res_headers_json": res_headers,
        "req_body_text": req_text,
        "req_body_mime": req_mime,
        "res_body_text": res_text,
        "res_body_mime": res_mime,
        "res_body_encoding": res_enc,
    }


def _iter_chunks(items: List[Any], chunk_size: int) -> Iterable[List[Any]]:
    if chunk_size <= 0:
        chunk_size = 1000
    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]


def _write_entries_jsonl(ctx: IngestContext) -> None:
    """Write entries to JSONL in APPLY mode, as-is, paginated.

    Controlled by HAR_ENTRIES_JSONL (default 0/off). Path via HAR_ENTRIES_JSONL_PATH
    (default databases/har_entries.ndjson). Chunk size uses HAR_ENTRIES_BATCH (default 1000).
    """
    if ctx.dry_run:
        return
    if os.environ.get("HAR_ENTRIES_JSONL", "0") in {"0", "false", "False", "no", "NO"}:
        return
    entries = ctx.raw_har.get("log", {}).get("entries") if ctx.raw_har else None
    if not isinstance(entries, list) or not entries:
        return
    target = os.environ.get("HAR_ENTRIES_JSONL_PATH", os.path.join("databases", "har_entries.ndjson"))
    path = Path(target)
    validate_no_forbidden_paths(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    batch = int(os.environ.get("HAR_ENTRIES_BATCH", "1000"))
    with open(path, "a", encoding="utf-8") as fh:
        for chunk in _iter_chunks(entries, batch):
            for e in chunk:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    # Path recorded via metrics summary below


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
        # Mitigate lock contention: small busy timeout
        try:
            cur.execute("PRAGMA busy_timeout=3000")
        except Exception:
            pass
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
        rows_all = [
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
        batch = int(os.environ.get("HAR_ENTRIES_BATCH", "1000"))
        for chunk in _iter_chunks(rows_all, batch):
            cur.executemany(
                """
                INSERT INTO har_entries (
                  started_at, method, url, host, path, status, status_text, mime_type,
                  wait_ms, blocked_ms, dns_ms, connect_ms, ssl_ms, send_ms, receive_ms, total_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                chunk,
            )
        # Persist headers/bodies into dedicated tables without altering content
        entries = ctx.raw_har.get("log", {}).get("entries") if ctx.raw_har else None
        if isinstance(entries, list) and entries and not ctx.dry_run:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS har_request_headers (
                  id INTEGER PRIMARY KEY,
                  entry_index INTEGER,
                  headers_json TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS har_response_headers (
                  id INTEGER PRIMARY KEY,
                  entry_index INTEGER,
                  headers_json TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS har_request_bodies (
                  id INTEGER PRIMARY KEY,
                  entry_index INTEGER,
                  body_text TEXT,
                  mime_type TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS har_response_bodies (
                  id INTEGER PRIMARY KEY,
                  entry_index INTEGER,
                  body_text TEXT,
                  mime_type TEXT,
                  encoding TEXT
                )
                """
            )

            redact_headers = os.environ.get("HAR_REDACT_HEADERS", "0") == "1"
            redact_bodies = os.environ.get("HAR_REDACT_BODIES", "0") == "1"
            req_hdr_rows: List[Tuple[int, str]] = []
            res_hdr_rows: List[Tuple[int, str]] = []
            req_body_rows: List[Tuple[int, Optional[str], str]] = []
            res_body_rows: List[Tuple[int, Optional[str], str, Optional[str]]] = []
            for idx, e in enumerate(entries):
                if not isinstance(e, dict):
                    continue
                parts = _extract_headers_and_bodies(e, redact_headers=redact_headers, redact_bodies=redact_bodies)
                if parts["req_headers_json"]:
                    req_hdr_rows.append((idx, json.dumps(parts["req_headers_json"], ensure_ascii=False)))
                if parts["res_headers_json"]:
                    res_hdr_rows.append((idx, json.dumps(parts["res_headers_json"], ensure_ascii=False)))
                if parts["req_body_text"] is not None or parts["req_body_mime"]:
                    req_body_rows.append((idx, parts["req_body_text"], parts["req_body_mime"]))
                if parts["res_body_text"] is not None or parts["res_body_mime"] or parts["res_body_encoding"] is not None:
                    res_body_rows.append((idx, parts["res_body_text"], parts["res_body_mime"], parts["res_body_encoding"]))
            if req_hdr_rows:
                cur.executemany(
                    "INSERT INTO har_request_headers (entry_index, headers_json) VALUES (?, ?)", req_hdr_rows
                )
            if res_hdr_rows:
                cur.executemany(
                    "INSERT INTO har_response_headers (entry_index, headers_json) VALUES (?, ?)", res_hdr_rows
                )
            if req_body_rows:
                cur.executemany(
                    "INSERT INTO har_request_bodies (entry_index, body_text, mime_type) VALUES (?, ?, ?)", req_body_rows
                )
            if res_body_rows:
                cur.executemany(
                    "INSERT INTO har_response_bodies (entry_index, body_text, mime_type, encoding) VALUES (?, ?, ?, ?)", res_body_rows
                )

        # Persist pages as JSON text, without alteration (no truncation, no summary)
        pages = ctx.raw_har.get("log", {}).get("pages") if ctx.raw_har else None
        if isinstance(pages, list) and pages:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS har_pages (
                  id INTEGER PRIMARY KEY,
                  page_index INTEGER,
                  page_json TEXT
                )
                """
            )
            chunk_size = int(os.environ.get("HAR_PAGES_CHUNK_SIZE", "1000"))
            for chunk_start, chunk in enumerate(_iter_chunks(pages, chunk_size)):
                rows_p = [
                    (i, json.dumps(p, ensure_ascii=False)) for i, p in enumerate(chunk, start=chunk_start * chunk_size)
                ]
                cur.executemany(
                    "INSERT INTO har_pages (page_index, page_json) VALUES (?, ?)", rows_p
                )
        conn.commit()
    finally:
        conn.close()


def _write_pages_jsonl(ctx: IngestContext) -> None:
    """Write pages to JSONL, each page as its original JSON, no modifications.

    Enabled only in APPLY mode. Path can be provided via HAR_PAGES_JSONL; if
    unset, defaults to databases/har_pages.ndjson.
    """
    if ctx.dry_run:
        return
    pages = ctx.raw_har.get("log", {}).get("pages") if ctx.raw_har else None
    if not isinstance(pages, list) or not pages:
        return
    # JSONL writing ON by default when APPLY=1; allow opt-out via HAR_PAGES_JSONL=0
    jsonl_enabled = os.environ.get("HAR_PAGES_JSONL", "1") not in {"0", "false", "False", "no", "NO"}
    if not jsonl_enabled:
        return
    target = os.environ.get("HAR_PAGES_JSONL_PATH", os.path.join("databases", "har_pages.ndjson"))
    target_path = Path(target)
    validate_no_forbidden_paths(str(target_path))
    target_path.parent.mkdir(parents=True, exist_ok=True)
    chunk_size = int(os.environ.get("HAR_PAGES_CHUNK_SIZE", "1000"))
    # Append to JSONL, preserving as-is JSON (ensure_ascii=False)
    with open(target_path, "a", encoding="utf-8") as fh:
        for chunk in _iter_chunks(pages, chunk_size):
            for p in chunk:
                fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    ctx.pages_jsonl_path = target_path


def _write_pages_preview_jsonl(ctx: IngestContext) -> None:
    """Write pages preview to .codex in DRY_RUN.

    - Enabled by default (HAR_PREVIEW_PAGES not set to 0).
    - Writes each page as-is (one per line) to `.codex/har_pages_preview.ndjson` unless
      HAR_PREVIEW_PAGES_JSONL overrides the path.
    """
    if not ctx.dry_run:
        return
    pages = ctx.raw_har.get("log", {}).get("pages") if ctx.raw_har else None
    if not isinstance(pages, list) or not pages:
        return
    preview_enabled = os.environ.get("HAR_PREVIEW_PAGES", "1") not in {"0", "false", "False", "no", "NO"}
    if not preview_enabled:
        return
    target = os.environ.get("HAR_PREVIEW_PAGES_JSONL", os.path.join(".codex", "har_pages_preview.ndjson"))
    target_path = Path(target)
    # Preview path is within the repo by default; still validate forbidden roots
    validate_no_forbidden_paths(str(target_path))
    target_path.parent.mkdir(parents=True, exist_ok=True)
    chunk_size = int(os.environ.get("HAR_PAGES_CHUNK_SIZE", "1000"))
    with open(target_path, "a", encoding="utf-8") as fh:
        for chunk in _iter_chunks(pages, chunk_size):
            for p in chunk:
                fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    ctx.pages_preview_jsonl_path = target_path


def _emit_metrics(ctx: IngestContext) -> None:
    record: Dict[str, Any] = {
        "event": "har_ingest",
        "ts": _iso_now(),
        "file": str(ctx.src_path),
        "total_entries": ctx.total_entries,
        "normalized_count": len(ctx.normalized or []),
        "pages_count": ctx.pages_count,
        "db_path": str(ctx.db_path),
        "dry_run": ctx.dry_run,
    }
    # Only emit creator/browser metadata when explicitly requested
    if os.environ.get("HAR_EMIT_META", "0") == "1":
        if ctx.meta_creator:
            record["creator"] = ctx.meta_creator
        if ctx.meta_browser:
            record["browser"] = ctx.meta_browser
    if ctx.pages_jsonl_path is not None:
        record["pages_jsonl_path"] = str(ctx.pages_jsonl_path)
    if ctx.pages_preview_jsonl_path is not None:
        record["pages_preview_jsonl_path"] = str(ctx.pages_preview_jsonl_path)
    # NDJSON summary & histogram (default on)
    if os.environ.get("NDJSON_SUMMARY", "1") not in {"0", "false", "False", "no", "NO"}:
        # Status histogram
        bins_str = os.environ.get("NDJSON_STATUS_BINS", "200,300,400,500")
        try:
            bounds = [int(x) for x in bins_str.split(",") if x.strip()]
        except Exception:
            bounds = [200, 300, 400, 500]
        statuses = [int(e.get("status", 0)) for e in (ctx.normalized or [])]
        hist: Dict[str, int] = {}
        prev = 0
        for b in bounds:
            label = f"lt{b}"
            hist[label] = sum(1 for s in statuses if prev <= s < b)
            prev = b
        hist[f"ge{prev}"] = sum(1 for s in statuses if s >= prev)
        record["status_histogram"] = hist
        # Chunk counts (derivable from env + sizes)
        try:
            entries_batch = int(os.environ.get("HAR_ENTRIES_BATCH", "1000"))
        except ValueError:
            entries_batch = 1000
        record["entries_batch_size"] = entries_batch
    append_ndjson(str(ctx.ndjson_path), record)


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
        StepCtx(name="PreviewPages", desc="Write pages to .codex JSONL (DRY_RUN)", fn=lambda: _write_pages_preview_jsonl(ctx)),
        StepCtx(name="PersistPages", desc="Write pages as JSONL and DB (APPLY)", fn=lambda: _write_pages_jsonl(ctx)),
        StepCtx(name="PersistEntriesJSONL", desc="Write entries JSONL (APPLY)", fn=lambda: _write_entries_jsonl(ctx)),
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
