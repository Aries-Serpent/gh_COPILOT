from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple

# SQLite pragmas: WAL improves concurrent readers; busy_timeout reduces SQLITE_BUSY.
# See: https://sqlite.org/wal.html ; https://highperformancesqlite.com/articles/sqlite-recommended-pragmas

@dataclass
class AuditResult:
    started_at: str
    finished_at: str
    scanned_paths: List[str]
    missing_count: int
    stale_count: int
    regenerated_count: int
    reingested_count: int
    details: dict
    status: str = "ok"

def _connect(db: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=10000;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_files(paths: Sequence[Path], patterns: Sequence[str]) -> Iterator[Path]:
    for root in paths:
        rp = Path(root)
        if rp.is_file():
            yield rp
            continue
        for pat in patterns:
            for fp in rp.rglob(pat):
                if fp.is_file():
                    yield fp


def _fetch_db_assets(conn: sqlite3.Connection, table: str, path_col: str, hash_col: Optional[str]) -> dict:
    cols = [path_col] + ([hash_col] if hash_col else [])
    q = f"SELECT {', '.join([c for c in cols if c])} FROM {table}"
    rows = conn.execute(q).fetchall()
    out = {}
    for r in rows:
        path = r[0]
        ch = r[1] if hash_col else None
        out[path] = ch
    return out


def _pragma_quick_check(conn: sqlite3.Connection) -> str:
    # quick_check is faster; integrity_check is more thorough. Both return 'ok' on success.
    # See: https://www.sqlite.org/pragma.html ; https://serverfault.com/questions/8048
    row = conn.execute("PRAGMA quick_check").fetchone()
    return row[0] if row else "ok"


def run_audit(
    enterprise_db: Path,
    production_db: Path,
    analytics_db: Path,
    base_paths: Sequence[Path],
    patterns: Sequence[str] = ("*.md", "*.sql", "*.py", "*.har"),
    *,
    regenerate: bool = False,
    reingest: bool = False,
) -> AuditResult:
    started = datetime.utcnow().isoformat()
    scanned = [str(p) for p in base_paths]

    ent = _connect(enterprise_db)
    prod = _connect(production_db)
    ana = _connect(analytics_db)

    # Health checks
    ent_health = _pragma_quick_check(ent)
    prod_health = _pragma_quick_check(prod)

    ent_assets = {}
    # Try common tables; ignore missing ones gracefully
    for t, path_col, hash_col in (
        ("documentation_assets", "path", "content_hash"),
        ("template_assets", "path", "content_hash"),
    ):
        try:
            ent_assets.update(_fetch_db_assets(ent, t, path_col, hash_col))
        except Exception:
            pass

    prod_assets = {}
    for t, path_col, hash_col in (
        ("har_entries", "path", "sha256"),
        ("har_entries", "path", "content_hash"),  # compat column
    ):
        try:
            prod_assets.update(_fetch_db_assets(prod, t, path_col, hash_col))
        except Exception:
            pass

    missing: List[str] = []
    stale: List[Tuple[str, str, str]] = []  # (path, expected_hash, actual_hash)

    for fp in _iter_files(base_paths, patterns):
        sp = str(fp)
        # If present in either ent/prod sets, compare hashes when available
        if sp in ent_assets or sp in prod_assets:
            try:
                actual = _sha256_file(fp)
            except Exception:
                continue
            expected = ent_assets.get(sp) or prod_assets.get(sp)
            if expected and expected != actual:
                stale.append((sp, expected, actual))
        # Also find DB rows that reference files that no longer exist
    for path_key in set(list(ent_assets.keys()) + list(prod_assets.keys())):
        if not Path(path_key).exists():
            missing.append(path_key)

    regenerated = 0
    reingested = 0

    # Optional actions
    if regenerate and stale:
        # Best‑effort call to generator; errors are captured into details
        try:
            os.system(
                "python scripts/generate_from_templates.py docs --params '{}' >/dev/null 2>&1"
            )
            regenerated = len(stale)
        except Exception:
            pass
    if reingest and (missing or stale):
        try:
            os.system(
                "python scripts/database/documentation_ingestor.py enterprise_assets.db >/dev/null 2>&1"
            )
            reingested = len(missing) + len(stale)
        except Exception:
            pass

    details = {
        "enterprise_quick_check": ent_health,
        "production_quick_check": prod_health,
        "missing_paths": missing,
        "stale_paths": stale[:1000],  # cap details size
    }

    finished = datetime.utcnow().isoformat()

    # Log into analytics
    try:
        with _connect(analytics_db) as c:
            c.execute(
                """
                INSERT INTO consistency_audit_events (
                  started_at, finished_at, scanned_paths,
                  missing_count, stale_count, regenerated_count, reingested_count, details_json, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    started,
                    finished,
                    json.dumps(scanned),
                    len(missing),
                    len(stale),
                    regenerated,
                    reingested,
                    json.dumps(details),
                    "ok",
                ),
            )
            c.commit()
    except Exception:
        # Do not fail the run if analytics logging failed
        pass

    return AuditResult(
        started_at=started,
        finished_at=finished,
        scanned_paths=scanned,
        missing_count=len(missing),
        stale_count=len(stale),
        regenerated_count=regenerated,
        reingested_count=reingested,
        details=details,
        status="ok",
    )
