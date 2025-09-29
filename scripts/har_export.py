#!/usr/bin/env python
from __future__ import annotations

"""Unified HAR DB exporter to JSONL (APPLY-only).

Exports rows from SQLite tables created by scripts/har_ingest.py into JSONL
files under an output directory. This script never modifies data; it transposes
tables to JSON lines exactly as stored.

Usage:
    python scripts/har_export.py --db databases/har_ingest.db --out exports

Env (optional):
- HAR_EXPORT_DIR: output directory (overridden by --out)
"""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

sys.path.insert(0, os.getcwd())
from gh_copilot.automation.guardrails import (  # type: ignore
    guard_no_github_actions,
    guard_no_recursive_backups,
    validate_no_forbidden_paths,
)


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


def _export_table_rows(db: Path, out_path: Path, query: str, row_to_json: Optional[Any] = None) -> int:
    conn = sqlite3.connect(str(db))
    count = 0
    try:
        cur = conn.cursor()
        cur.execute(query)
        cols = [d[0] for d in cur.description]
        with open(out_path, "w", encoding="utf-8") as fh:
            for row in cur:
                if row_to_json is not None:
                    obj = row_to_json(row)
                else:
                    obj = {k: row[i] for i, k in enumerate(cols)}
                fh.write(json.dumps(obj, ensure_ascii=False) + "\n")
                count += 1
        return count
    finally:
        conn.close()


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", dest="db_path", required=True, help="SQLite database path")
    parser.add_argument("--out", dest="out_dir", default=None, help="Output directory (JSONL)")
    args = parser.parse_args(list(argv) if argv is not None else None)

    db_path = Path(args.db_path).resolve()
    if not db_path.exists():
        print(f"DB not found: {db_path}", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir or os.environ.get("HAR_EXPORT_DIR", "exports")).resolve()

    repo_root = _git_root_fallback()
    guard_no_recursive_backups(str(repo_root))
    guard_no_github_actions(str(repo_root))
    validate_no_forbidden_paths(str(out_dir))
    out_dir.mkdir(parents=True, exist_ok=True)

    # Export entries
    entries_jsonl = out_dir / "har_entries.ndjson"
    pages_jsonl = out_dir / "har_pages.ndjson"
    req_hdr_jsonl = out_dir / "har_request_headers.ndjson"
    res_hdr_jsonl = out_dir / "har_response_headers.ndjson"
    req_body_jsonl = out_dir / "har_request_bodies.ndjson"
    res_body_jsonl = out_dir / "har_response_bodies.ndjson"

    total = 0

    def _row_pages(row):
        # row = (id, page_index, page_json) → write page_json object
        try:
            return json.loads(row[2] or "{}")
        except Exception:
            return {"page_index": row[1], "page_json": row[2]}

    if True:
        # har_entries
        if _table_exists(db_path, "har_entries"):
            total += _export_table_rows(db_path, entries_jsonl, "SELECT * FROM har_entries")
        # har_pages
        if _table_exists(db_path, "har_pages"):
            total += _export_table_rows(db_path, pages_jsonl, "SELECT * FROM har_pages", row_to_json=_row_pages)
        # headers
        if _table_exists(db_path, "har_request_headers"):
            total += _export_table_rows(db_path, req_hdr_jsonl, "SELECT entry_index, headers_json FROM har_request_headers")
        if _table_exists(db_path, "har_response_headers"):
            total += _export_table_rows(db_path, res_hdr_jsonl, "SELECT entry_index, headers_json FROM har_response_headers")
        # bodies
        if _table_exists(db_path, "har_request_bodies"):
            total += _export_table_rows(db_path, req_body_jsonl, "SELECT entry_index, body_text, mime_type FROM har_request_bodies")
        if _table_exists(db_path, "har_response_bodies"):
            total += _export_table_rows(db_path, res_body_jsonl, "SELECT entry_index, body_text, mime_type, encoding FROM har_response_bodies")

    print(json.dumps({"ok": True, "exported_lines": total, "out_dir": str(out_dir)}))
    return 0


def _table_exists(db: Path, name: str) -> bool:
    conn = sqlite3.connect(str(db))
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
        return cur.fetchone() is not None
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())

