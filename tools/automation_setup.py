from __future__ import annotations

import hashlib
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

from utils.log_utils import _log_event, DEFAULT_ANALYTICS_DB
from secondary_copilot_validator import SecondaryCopilotValidator

DB_PATH = Path("databases/production.db")
ANALYTICS_DB = DEFAULT_ANALYTICS_DB
DOC_DIRS = [Path("documentation"), Path("docs")]
TEMPLATE_DIRS = [Path("prompts"), Path("template_engine/templates")]


def init_databases() -> None:
    if not DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS documentation_assets ("
            "id INTEGER PRIMARY KEY,"
            "doc_path TEXT NOT NULL,"
            "content_hash TEXT NOT NULL,"
            "created_at TEXT NOT NULL,"
            "modified_at TEXT NOT NULL"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS template_assets ("
            "id INTEGER PRIMARY KEY,"
            "template_path TEXT NOT NULL,"
            "content_hash TEXT NOT NULL,"
            "created_at TEXT NOT NULL"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS pattern_assets ("
            "id INTEGER PRIMARY KEY,"
            "pattern TEXT NOT NULL,"
            "usage_count INTEGER DEFAULT 0,"
            "created_at TEXT NOT NULL"
            ")"
        )
        conn.commit()
        conn.close()


def ingest_assets() -> None:
    _log_event({"event": "ingestion_started"}, db_path=ANALYTICS_DB)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    doc_files = []
    for d in DOC_DIRS:
        if d.exists():
            doc_files.extend(sorted(p for p in d.rglob("*.md") if p.is_file()))

    tmpl_files = []
    for d in TEMPLATE_DIRS:
        if d.exists():
            tmpl_files.extend(sorted(p for p in d.rglob("*.md") if p.is_file()))

    start_docs = datetime.now(timezone.utc)
    with tqdm(total=len(doc_files), desc="Docs", unit="file") as bar:
        for path in doc_files:
            if path.stat().st_size == 0:
                bar.update(1)
                continue
            content = path.read_text(encoding="utf-8")
            digest = hashlib.sha256(content.encode()).hexdigest()
            modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
            cur.execute(
                "INSERT INTO documentation_assets (doc_path, content_hash, created_at, modified_at)"
                " VALUES (?, ?, ?, ?)",
                (
                    str(path),
                    digest,
                    datetime.now(timezone.utc).isoformat(),
                    modified,
                ),
            )
            bar.update(1)
    conn.commit()
    _log_event({"event": "docs_ingested", "count": len(doc_files)}, db_path=ANALYTICS_DB)

    start_tpl = datetime.now(timezone.utc)
    with tqdm(total=len(tmpl_files), desc="Templates", unit="file") as bar:
        for path in tmpl_files:
            content = path.read_text(encoding="utf-8")
            digest = hashlib.sha256(content.encode()).hexdigest()
            cur.execute(
                "INSERT INTO template_assets (template_path, content_hash, created_at)"
                " VALUES (?, ?, ?)",
                (
                    str(path),
                    digest,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            cur.execute(
                "INSERT INTO pattern_assets (pattern, usage_count, created_at)"
                " VALUES (?, 0, ?)",
                (content[:1000], datetime.now(timezone.utc).isoformat()),
            )
            bar.update(1)
    conn.commit()
    conn.close()
    _log_event({"event": "templates_ingested", "count": len(tmpl_files)}, db_path=ANALYTICS_DB)
    _log_event({"event": "ingestion_completed", "docs": len(doc_files), "templates": len(tmpl_files)}, db_path=ANALYTICS_DB)

    SecondaryCopilotValidator().validate_corrections(
        [str(p) for p in doc_files + tmpl_files]
    )


def run_audit() -> None:
    os.system('python scripts/code_placeholder_audit.py')


if __name__ == '__main__':
    start = datetime.now(timezone.utc)
    _log_event({"event": "automation_setup_start"}, db_path=ANALYTICS_DB)
    init_databases()
    ingest_assets()
    run_audit()
    duration = (datetime.now(timezone.utc) - start).total_seconds()
    _log_event({"event": "automation_setup_end", "duration": duration}, db_path=ANALYTICS_DB)
    print(f"Automation finished in {duration}s")
