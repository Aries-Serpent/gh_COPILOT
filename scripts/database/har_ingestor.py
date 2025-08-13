#!/usr/bin/env python3
from __future__ import annotations
import json, os, sqlite3, sys, hashlib
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator, Iterable
import typer

PRAGMAS: tuple[str, ...] = (
    "PRAGMA journal_mode=WAL;",
    "PRAGMA synchronous=NORMAL;",
    "PRAGMA foreign_keys=ON;",
    "PRAGMA busy_timeout=10000;",
)

@contextmanager
def connect(db: Path) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    for p in PRAGMAS:
        conn.execute(p)
    try:
        yield conn
    finally:
        conn.close()

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def discover(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for base in paths:
        if base.is_file() and base.suffix.lower() == ".har":
            out.append(base)
        elif base.is_dir():
            out.extend([p for p in base.rglob("*.har") if p.is_file()])
    return out

def parse_metrics(p: Path) -> dict:
    try:
        obj = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
        entries = obj.get("log", {}).get("entries", [])
        total_entries = len(entries)
        # Approximate total size using file size (fast & robust)
        size_bytes = p.stat().st_size
        return {"entries": total_entries, "size_bytes": size_bytes}
    except Exception:
        return {"entries": None, "size_bytes": p.stat().st_size}

def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS har_entries (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          path TEXT NOT NULL,
          sha256 TEXT NOT NULL,
          created_at TEXT NOT NULL,
          metrics_json TEXT
        );
        CREATE UNIQUE INDEX IF NOT EXISTS ux_har_entries_path_sha ON har_entries(path, sha256);
        """
    )

def ingest(db: Path, items: Iterable[Path], checkpoint: bool = False) -> int:
    with connect(db) as c:
        ensure_schema(c)
        rows = []
        now = datetime.utcnow().isoformat()
        for p in items:
            rows.append((str(p), sha256_file(p), now, json.dumps(parse_metrics(p))))
        if not rows:
            return 0
        # Batched transaction
        with c:
            c.executemany(
                "INSERT OR IGNORE INTO har_entries(path, sha256, created_at, metrics_json) VALUES (?,?,?,?)",
                rows,
            )
        if checkpoint:
            try:
                c.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            except Exception:
                pass
        return len(rows)

app = typer.Typer(add_completion=False, help="HAR ingestor with WAL + busy_timeout + batching")

@app.command()
def main(
    db: Path = typer.Option(Path("analytics.db"), help="Target SQLite"),
    path: list[Path] = typer.Argument(..., help="HAR files or directories"),
    checkpoint: bool = typer.Option(False, help="Run PRAGMA wal_checkpoint(TRUNCATE) after ingest"),
) -> None:
    items = discover(list(path))
    count = ingest(db, items, checkpoint=checkpoint or (os.getenv("GH_COPILOT_WAL_CHECKPOINT", "0") in {"1","true","on"}))
    print(json.dumps({"ingested": count, "db": str(db)}, indent=2))

if __name__ == "__main__":
    app()
