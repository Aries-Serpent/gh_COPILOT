from __future__ import annotations
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .dao import IngestDAO

PRAGMAS = (
    "PRAGMA journal_mode=WAL;",
    "PRAGMA synchronous=NORMAL;",
    "PRAGMA foreign_keys=ON;",
    "PRAGMA busy_timeout=10000;",
)

@dataclass
class IngestResult:
    inserted: int
    skipped: int
    errors: int
    duration_s: float
    checkpointed: bool


def _connect(db: Path) -> sqlite3.Connection:
    c = sqlite3.connect(db)
    c.row_factory = sqlite3.Row
    for p in PRAGMAS:
        c.execute(p)
    return c


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS har_entries (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          path TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        """
    )
    cols = {r[1] for r in conn.execute("PRAGMA table_info(har_entries)")}
    if "sha256" not in cols:
        conn.execute("ALTER TABLE har_entries ADD COLUMN sha256 TEXT")
    if "content_hash" not in cols:
        conn.execute("ALTER TABLE har_entries ADD COLUMN content_hash TEXT")
    if "metrics_json" not in cols:
        conn.execute("ALTER TABLE har_entries ADD COLUMN metrics_json TEXT")
    if "metrics" not in cols:
        conn.execute("ALTER TABLE har_entries ADD COLUMN metrics TEXT")
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_har_entries_path_hash ON har_entries(path, COALESCE(sha256, content_hash))"
    )


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _discover(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for base in paths:
        if base.is_file() and base.suffix.lower() == ".har":
            out.append(base)
        elif base.is_dir():
            out.extend([p for p in base.rglob("*.har") if p.is_file()])
    return out


def _parse_metrics(p: Path) -> dict:
    try:
        obj = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
        entries = obj.get("log", {}).get("entries", [])
        total_entries = len(entries)
        size_bytes = p.stat().st_size
        return {"entries": total_entries, "size_bytes": size_bytes}
    except Exception:
        return {"entries": None, "size_bytes": p.stat().st_size}


def ingest_har_entries(db_path: str | Path, inputs: Iterable[str | Path], *, checkpoint: bool = False) -> IngestResult:
    import time

    start = time.perf_counter()
    db = Path(db_path)
    paths = [Path(x) for x in inputs]
    files = _discover(paths)
    inserted = errors = 0
    dao = IngestDAO(db)
    with _connect(db) as c:
        _ensure_schema(c)
        now = datetime.utcnow().isoformat()
        with c:
            for f in files:
                try:
                    h = _sha256_file(f)
                    metrics = _parse_metrics(f)
                    c.execute(
                        "INSERT OR IGNORE INTO har_entries(path, sha256, content_hash, created_at, metrics_json, metrics) VALUES (?,?,?,?,?,?)",
                        (str(f), h, h, now, json.dumps(metrics), json.dumps(metrics)),
                    )
                    inserted_rows = c.rowcount
                    rowid = c.execute(
                        "SELECT id FROM har_entries WHERE path=? AND COALESCE(sha256, content_hash)=?",
                        (str(f), h),
                    ).fetchone()[0]
                    status_flag = "ok" if inserted_rows > 0 else "skipped"
                    dao.log_event(
                        kind="har",
                        source=str(f),
                        target_table="har_entries",
                        target_pk=rowid,
                        status=status_flag,
                        sha256=h,
                        metrics=metrics,
                        connection=c,
                    )
                    if status_flag == "ok":
                        inserted += 1
                except Exception as exc:
                    errors += 1
                    dao.log_event(
                        kind="har",
                        source=str(f),
                        target_table="har_entries",
                        target_pk=None,
                        status="error",
                        metrics={"error": str(exc)},
                        connection=c,
                    )
        if checkpoint:
            try:
                c.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            except Exception:
                pass
    dur = time.perf_counter() - start
    return IngestResult(
        inserted=inserted,
        skipped=len(files) - inserted,
        errors=errors,
        duration_s=dur,
        checkpointed=checkpoint,
    )
