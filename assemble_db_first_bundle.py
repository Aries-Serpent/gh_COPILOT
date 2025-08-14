"""Assemble the DB-first bundle into a directory and zip archive.

This script recreates a minimal DB-first scaffold by copying selected
repository files into a fresh ``db_first_bundle`` folder and then
compressing that folder into ``db_first_bundle.zip``.  It mirrors the
behavior of the original one-shot assembler while using relative paths
instead of hard-coded locations.
"""
# Rebuild the scaffold directory and ZIP it using Python's zipfile.
from pathlib import Path
import zipfile
import json

root = Path("/mnt/data/db_first_bundle")
zip_path = Path("/mnt/data/db_first_bundle.zip")

# Clean & recreate target folder
if root.exists():
    for p in sorted(root.rglob("*"), reverse=True):
        try:
            if p.is_file():
                p.unlink()
            else:
                p.rmdir()
        except Exception:
            pass
root.mkdir(parents=True, exist_ok=True)

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

# ---------------- Files content (corrected & runnable) ----------------

asset_ingestor_base_py = r'''#!/usr/bin/env python3
"""
Reusable base class for DB-first asset ingestion.
- Walks a root directory for matching patterns
- Hashes files (SHA-256)
- Deduplicates (via subclass-provided unique predicate)
- Batches inserts in transactions
- Logs analytics events to analytics.db:event_log (auto-creates if missing)
- Uses SQLite WAL + busy_timeout for concurrency
"""
from __future__ import annotations

import dataclasses
import fnmatch
import hashlib
import json
import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

CHUNK_SIZE = 1024 * 1024  # 1 MiB
DEFAULT_BATCH_SIZE = 200
DEFAULT_BUSY_TIMEOUT_MS = 10_000
WAL_CHECKPOINT_THRESHOLD_BYTES = 64 * 1024 * 1024  # 64 MiB


@dataclass
class IngestSummary:
    kind: str
    table: str
    inserted: int = 0
    duplicates: int = 0
    skipped_zero: int = 0
    errors: list = dataclasses.field(default_factory=list)
    duration_ms: int = 0

    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self), indent=2)


class AssetIngestorBase:
    """Base class to standardize ingestion behavior.

    Subclasses must override:
      - table_name()
      - schema_sql()
      - row_for(file_path, content_hash, stat)
      - unique_predicate()
    Optionally override on_after_insert(row_id, file_path, row_dict).
    """

    kind: str = "asset"
    patterns: Sequence[str] = ()

    def __init__(
        self,
        root_dir: Path,
        db_path: Path,
        analytics_db_path: Optional[Path] = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
        busy_timeout_ms: int = DEFAULT_BUSY_TIMEOUT_MS,
    ) -> None:
        self.root_dir = Path(root_dir)
        self.db_path = Path(db_path)
        self.analytics_db_path = Path(analytics_db_path) if analytics_db_path else None
        self.batch_size = batch_size
        self.busy_timeout_ms = busy_timeout_ms

        if not self.root_dir.exists():
            raise FileNotFoundError(f"root_dir does not exist: {self.root_dir}")

    # ---- hooks to override ----
    def table_name(self) -> str:
        raise NotImplementedError

    def schema_sql(self) -> Sequence[str]:
        return ()

    def row_for(self, file_path: str, content_hash: str, stat: os.stat_result) -> dict:
        raise NotImplementedError

    def unique_predicate(self) -> str:
        raise NotImplementedError

    def on_after_insert(self, row_id: int, file_path: str, row: dict) -> None:
        return None

    # ---- core helpers ----
    def _connect(self, path: Path) -> sqlite3.Connection:
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(path))
        with conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute(f"PRAGMA busy_timeout={int(self.busy_timeout_ms)};")
            conn.execute("PRAGMA foreign_keys=ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_analytics(self, conn: sqlite3.Connection) -> None:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS event_log (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  ts TEXT NOT NULL,
                  kind TEXT NOT NULL,
                  payload TEXT NOT NULL
                );
                """
            )

    def _log_event(self, kind: str, payload: dict) -> None:
        if not self.analytics_db_path:
            return
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._connect(self.analytics_db_path) as ac:
            self._ensure_analytics(ac)
            with ac:
                ac.execute(
                    "INSERT INTO event_log(ts, kind, payload) VALUES(?,?,?)",
                    (ts, kind, json.dumps(payload, ensure_ascii=False)),
                )

    def _match(self, rel: str) -> bool:
        if not self.patterns:
            return True
        return any(fnmatch.fnmatch(rel, pat) for pat in self.patterns)

    def discover_files(self) -> List[Path]:
        files: List[Path] = []
        base = self.root_dir
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            rel = str(p.relative_to(base))
            if self._match(rel):
                try:
                    _ = p.stat()  # may raise if file removed
                    files.append(p)
                except FileNotFoundError:
                    continue
        files.sort()
        return files

    def hash_file(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                h.update(chunk)
        return h.hexdigest()

    def wal_checkpoint_if_large(self, conn: sqlite3.Connection) -> None:
        wal_path = Path(str(self.db_path) + "-wal")
        try:
            if wal_path.exists() and wal_path.stat().st_size > WAL_CHECKPOINT_THRESHOLD_BYTES:
                with conn:
                    conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        except Exception:
            pass

    # ---- main ingest ----
    def ingest(self) -> IngestSummary:
        t0 = time.time()
        summary = IngestSummary(kind=self.kind, table=self.table_name())
        files = self.discover_files()

        with self._connect(self.db_path) as conn:
            with conn:
                for ddl in self.schema_sql():
                    conn.execute(ddl)

            batch: List[Tuple[Path, dict]] = []
            for p in files:
                try:
                    st = p.stat()
                    if st.st_size == 0:
                        summary.skipped_zero += 1
                        continue
                    ch = self.hash_file(p)
                    row = self.row_for(str(p), ch, st)
                    # Duplicate check
                    with conn:
                        cur = conn.execute(
                            f"SELECT 1 FROM {self.table_name()} WHERE {self.unique_predicate()} LIMIT 1",
                            row,
                        )
                        if cur.fetchone() is not None:
                            summary.duplicates += 1
                            continue
                    batch.append((p, row))

                    if len(batch) >= self.batch_size:
                        self._flush_batch(conn, batch, summary)
                        batch.clear()
                except Exception as e:
                    summary.errors.append({"file": str(p), "error": repr(e)})

            if batch:
                self._flush_batch(conn, batch, summary)
            self.wal_checkpoint_if_large(conn)

        summary.duration_ms = int((time.time() - t0) * 1000)
        self._log_event(
            kind="asset_ingest",
            payload={
                "kind": self.kind,
                "table": self.table_name(),
                "inserted": summary.inserted,
                "duplicates": summary.duplicates,
                "skipped_zero": summary.skipped_zero,
                "errors": summary.errors,
                "duration_ms": summary.duration_ms,
            },
        )
        return summary

    def _flush_batch(self, conn: sqlite3.Connection, batch: List[Tuple[Path, dict]], summary: IngestSummary) -> None:
        with conn:
            for p, row in batch:
                cols = ", ".join(row.keys())
                vals = ":" + ", :".join(row.keys())
                sql = f"INSERT INTO {self.table_name()} ({cols}) VALUES ({vals})"
                cur = conn.execute(sql, row)
                rid = int(cur.lastrowid)
                self.on_after_insert(rid, str(p), row)
                summary.inserted += 1


if __name__ == "__main__":
    print("This module is a base class. Use concrete ingestors like har_asset_ingestor.py or shell_log_ingestor.py to run.")
'''

har_asset_ingestor_py = r'''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from scripts.database.lib.asset_ingestor_base import AssetIngestorBase


class HarAssetIngestor(AssetIngestorBase):
    kind = "har"
    patterns: Sequence[str] = ("**/*.har",)

    def table_name(self) -> str:
        return "har_entries"

    def schema_sql(self):
        return (
            """
            CREATE TABLE IF NOT EXISTS har_entries (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              file_path TEXT NOT NULL UNIQUE,
              content_hash TEXT NOT NULL,
              size_bytes INTEGER NOT NULL,
              pages_count INTEGER,
              entries_count INTEGER,
              total_bytes INTEGER,
              total_duration_ms INTEGER,
              created_at TEXT NOT NULL,
              modified_at TEXT NOT NULL,
              raw_har_json TEXT
            );
            """,
            "CREATE INDEX IF NOT EXISTS idx_har_hash ON har_entries(content_hash);",
            "CREATE INDEX IF NOT EXISTS idx_har_created ON har_entries(created_at);",
        )

    def unique_predicate(self) -> str:
        return "file_path = :file_path"

    def _utc_now(self) -> str:
        import time
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def row_for(self, file_path: str, content_hash: str, stat: os.stat_result) -> dict:
        pages_count = None
        entries_count = None
        total_bytes = None
        total_duration_ms = None
        raw_json_text = None
        try:
            text = Path(file_path).read_text(encoding="utf-8")
            data = json.loads(text)
            log = data.get("log", {}) if isinstance(data, dict) else {}
            pages = log.get("pages", []) or []
            entries = log.get("entries", []) or []
            pages_count = len(pages)
            entries_count = len(entries)
            tbytes = 0
            for e in entries:
                resp = e.get("response", {}) if isinstance(e, dict) else {}
                bs = resp.get("bodySize")
                if isinstance(bs, int) and bs >= 0:
                    tbytes += bs
            total_bytes = tbytes

            import datetime
            def parse_dt(s: str):
                try:
                    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
                except Exception:
                    return None
            starts = []
            ends = []
            for e in entries:
                s = e.get("startedDateTime")
                if isinstance(s, str):
                    dt = parse_dt(s)
                    if dt:
                        starts.append(dt)
                ts = e.get("time")
                if (starts) and isinstance(ts, (int, float)):
                    ends.append(starts[-1] + datetime.timedelta(milliseconds=float(ts)))
            if starts and ends:
                total_duration_ms = int((max(ends) - min(starts)).total_seconds() * 1000)
            else:
                total_duration_ms = 0
            if stat.st_size <= 50 * 1024 * 1024:
                raw_json_text = text
        except Exception:
            pass

        ts = self._utc_now()
        return {
            "file_path": file_path,
            "content_hash": content_hash,
            "size_bytes": int(stat.st_size),
            "pages_count": pages_count,
            "entries_count": entries_count,
            "total_bytes": total_bytes,
            "total_duration_ms": total_duration_ms,
            "created_at": ts,
            "modified_at": ts,
            "raw_har_json": raw_json_text,
        }


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest HAR files into enterprise_assets.db")
    ap.add_argument("--root", required=True, help="Root directory to scan (e.g., har/)")
    ap.add_argument("--db", required=True, help="Path to enterprise_assets.db")
    ap.add_argument("--analytics", required=False, help="Path to analytics.db for event logging")
    ap.add_argument("--batch-size", type=int, default=200)
    ns = ap.parse_args()

    ing = HarAssetIngestor(
        root_dir=Path(ns.root),
        db_path=Path(ns.db),
        analytics_db_path=Path(ns.analytics) if ns.analytics else None,
        batch_size=ns.batch_size,
    )
    summary = ing.ingest()
    print(summary.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

shell_log_ingestor_py = r'''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from typing import Sequence

from scripts.database.lib.asset_ingestor_base import AssetIngestorBase


SESSION_RE = re.compile(r"(?P<source>[^_\s]+)__session_(?P<sid>[0-9T:-]+)")


class ShellLogIngestor(AssetIngestorBase):
    kind = "shell_log"
    patterns: Sequence[str] = ("**/*.log", "**/*.out", "**/*.txt")

    def table_name(self) -> str:
        return "shell_logs"

    def schema_sql(self):
        return (
            """
            CREATE TABLE IF NOT EXISTS shell_logs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              file_path TEXT NOT NULL UNIQUE,
              content_hash TEXT NOT NULL,
              size_bytes INTEGER NOT NULL,
              source TEXT,
              session_id TEXT,
              created_at TEXT NOT NULL,
              modified_at TEXT NOT NULL,
              log_text TEXT
            );
            """,
            "CREATE INDEX IF NOT EXISTS idx_shell_hash ON shell_logs(content_hash);",
            "CREATE INDEX IF NOT EXISTS idx_shell_session ON shell_logs(session_id);",
        )

    def unique_predicate(self) -> str:
        return "file_path = :file_path"

    def _utc_now(self) -> str:
        import time
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def _extract_meta(self, file_path: str):
        name = Path(file_path).name
        m = SESSION_RE.search(name)
        if not m:
            return None, None
        return m.group("source"), m.group("sid")

    def row_for(self, file_path: str, content_hash: str, stat: os.stat_result) -> dict:
        text: str | None = None
        try:
            limit = 5 * 1024 * 1024  # 5MB
            with Path(file_path).open("rb") as f:
                b = f.read(limit)
            text = b.decode("utf-8", errors="replace")
            if stat.st_size > limit:
                text += "\n[...truncated...]\n"
        except Exception:
            text = None
        src, sid = self._extract_meta(file_path)
        ts = self._utc_now()
        return {
            "file_path": file_path,
            "content_hash": content_hash,
            "size_bytes": int(stat.st_size),
            "source": src,
            "session_id": sid,
            "created_at": ts,
            "modified_at": ts,
            "log_text": text,
        }


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest shell/CLI logs into enterprise_assets.db")
    ap.add_argument("--root", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--analytics", required=False)
    ap.add_argument("--batch-size", type=int, default=200)
    ns = ap.parse_args()

    ing = ShellLogIngestor(
        root_dir=Path(ns.root),
        db_path=Path(ns.db),
        analytics_db_path=Path(ns.analytics) if ns.analytics else None,
        batch_size=ns.batch_size,
    )
    summary = ing.ingest()
    print(summary.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

documentation_ingestor_py = r'''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Sequence

from scripts.database.lib.asset_ingestor_base import AssetIngestorBase


class DocumentationIngestor(AssetIngestorBase):
    kind = "documentation"
    patterns: Sequence[str] = ("**/*.md", "**/*.markdown")

    def __init__(
        self,
        root_dir: Path,
        db_path: Path,
        analytics_db_path: Path | None = None,
        batch_size: int = 200,
        busy_timeout_ms: int = 10_000,
        versioning: bool = True,
        update_in_place: bool = False,
    ) -> None:
        super().__init__(root_dir, db_path, analytics_db_path, batch_size, busy_timeout_ms)
        self.versioning = versioning and not update_in_place
        self.update_in_place = update_in_place

    def table_name(self) -> str:
        return "documentation_assets"

    def schema_sql(self):
        return (
            """
            CREATE TABLE IF NOT EXISTS documentation_assets (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              doc_path TEXT NOT NULL,
              content_hash TEXT NOT NULL,
              size_bytes INTEGER NOT NULL,
              version INTEGER NOT NULL DEFAULT 1,
              created_at TEXT NOT NULL,
              modified_at TEXT NOT NULL
            );
            """,
            """
            CREATE VIEW IF NOT EXISTS v_documentation_assets_latest AS
            SELECT da.* FROM documentation_assets da
            WHERE da.id IN (
              SELECT id FROM (
                SELECT id, doc_path, version, ROW_NUMBER() OVER (
                  PARTITION BY doc_path ORDER BY version DESC, id DESC
                ) AS rn
                FROM documentation_assets
              ) WHERE rn = 1
            );
            """,
            "CREATE INDEX IF NOT EXISTS idx_docs_path ON documentation_assets(doc_path);",
            "CREATE INDEX IF NOT EXISTS idx_docs_hash ON documentation_assets(content_hash);",
        )

    def unique_predicate(self) -> str:
        return "doc_path = :doc_path AND content_hash = :content_hash"

    def _utc_now(self) -> str:
        import time
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def row_for(self, file_path: str, content_hash: str, stat: os.stat_result) -> dict:
        ts = self._utc_now()
        rel = str(Path(file_path).relative_to(self.root_dir)).replace(os.sep, "/")
        return {
            "doc_path": rel,
            "content_hash": content_hash,
            "size_bytes": int(stat.st_size),
            "version": 1,
            "created_at": ts,
            "modified_at": ts,
        }

    def ingest(self):
        from scripts.database.lib.asset_ingestor_base import IngestSummary
        import time

        t0 = time.time()
        files = self.discover_files()
        s = IngestSummary(kind=self.kind, table=self.table_name())

        with self._connect(self.db_path) as conn:
            for ddl in self.schema_sql():
                with conn:
                    conn.execute(ddl)
            for p in files:
                try:
                    st = p.stat()
                    if st.st_size == 0:
                        s.skipped_zero += 1
                        continue
                    ch = self.hash_file(p)
                    rel = str(p.relative_to(self.root_dir)).replace(os.sep, "/")
                    ts = self._utc_now()
                    cur = conn.execute(
                        "SELECT id, content_hash, version FROM documentation_assets WHERE doc_path=? ORDER BY version DESC, id DESC LIMIT 1",
                        (rel,),
                    )
                    row = cur.fetchone()
                    if row is None:
                        with conn:
                            conn.execute(
                                "INSERT INTO documentation_assets(doc_path, content_hash, size_bytes, version, created_at, modified_at) VALUES(?,?,?,?,?,?)",
                                (rel, ch, int(st.st_size), 1, ts, ts),
                            )
                        s.inserted += 1
                        continue
                    latest_hash = row["content_hash"]
                    latest_ver = int(row["version"])
                    if latest_hash == ch:
                        s.duplicates += 1
                        continue
                    if self.update_in_place:
                        with conn:
                            conn.execute(
                                "UPDATE documentation_assets SET content_hash=?, size_bytes=?, modified_at=? WHERE id=?",
                                (ch, int(st.st_size), ts, int(row["id"])),
                            )
                        s.inserted += 1
                    else:
                        with conn:
                            conn.execute(
                                "INSERT INTO documentation_assets(doc_path, content_hash, size_bytes, version, created_at, modified_at) VALUES(?,?,?,?,?,?)",
                                (rel, ch, int(st.st_size), latest_ver + 1, ts, ts),
                            )
                        s.inserted += 1
                except Exception as e:
                    s.errors.append({"file": str(p), "error": repr(e)})
            self.wal_checkpoint_if_large(conn)
        s.duration_ms = int((time.time() - t0) * 1000)
        self._log_event(
            "asset_ingest",
            {
                "kind": self.kind,
                "table": self.table_name(),
                "inserted": s.inserted,
                "duplicates": s.duplicates,
                "skipped_zero": s.skipped_zero,
                "errors": s.errors,
                "duration_ms": s.duration_ms,
                "versioning": self.versioning,
                "update_in_place": self.update_in_place,
            },
        )
        return s


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest Markdown docs with versioning support")
    ap.add_argument("--root", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--analytics")
    ap.add_argument("--no-versioning", action="store_true", help="Disable versioning")
    ap.add_argument("--in-place", action="store_true", help="Update latest row instead of version bump")
    ns = ap.parse_args()

    ing = DocumentationIngestor(
        root_dir=Path(ns.root),
        db_path=Path(ns.db),
        analytics_db_path=Path(ns.analytics) if ns.analytics else None,
        versioning=not ns.no_versioning and not ns.update_in_place,
        update_in_place=ns.update_in_place,
    )
    summary = ing.ingest()
    print(summary.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

migration_sql = r'''-- Idempotent SQLite migration for enterprise_assets.db
PRAGMA foreign_keys=ON;

-- HAR entries
CREATE TABLE IF NOT EXISTS har_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_path TEXT NOT NULL UNIQUE,
  content_hash TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  pages_count INTEGER,
  entries_count INTEGER,
  total_bytes INTEGER,
  total_duration_ms INTEGER,
  created_at TEXT NOT NULL,
  modified_at TEXT NOT NULL,
  raw_har_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_har_hash ON har_entries(content_hash);
CREATE INDEX IF NOT EXISTS idx_har_created ON har_entries(created_at);

-- Shell logs
CREATE TABLE IF NOT EXISTS shell_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_path TEXT NOT NULL UNIQUE,
  content_hash TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  source TEXT,
  session_id TEXT,
  created_at TEXT NOT NULL,
  modified_at TEXT NOT NULL,
  log_text TEXT
);
CREATE INDEX IF NOT EXISTS idx_shell_hash ON shell_logs(content_hash);
CREATE INDEX IF NOT EXISTS idx_shell_session ON shell_logs(session_id);

-- Documentation versioning
-- Add column if missing
ALTER TABLE documentation_assets ADD COLUMN version INTEGER NOT NULL DEFAULT 1;

-- Latest-view (safe to create if missing)
CREATE VIEW IF NOT EXISTS v_documentation_assets_latest AS
SELECT da.* FROM documentation_assets da
WHERE da.id IN (
  SELECT id FROM (
    SELECT id, doc_path, version, ROW_NUMBER() OVER (
      PARTITION BY doc_path ORDER BY version DESC, id DESC
    ) AS rn
    FROM documentation_assets
  ) WHERE rn = 1
);
'''

initializer_py = r'''#!/usr/bin/env python3
"""Ensure enterprise_assets.db has required tables for assets."""
from __future__ import annotations
import sqlite3, os
from pathlib import Path

ENTERPRISE_DB = Path(os.getenv("ENTERPRISE_ASSETS_DB", "enterprise_assets.db"))

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS documentation_assets (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      doc_path TEXT NOT NULL,
      content_hash TEXT NOT NULL,
      size_bytes INTEGER NOT NULL,
      version INTEGER NOT NULL DEFAULT 1,
      created_at TEXT NOT NULL,
      modified_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS template_assets (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      template_path TEXT NOT NULL,
      content_hash TEXT NOT NULL,
      size_bytes INTEGER NOT NULL,
      created_at TEXT NOT NULL,
      modified_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS pattern_assets (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      template_path TEXT NOT NULL,
      snippet TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS har_entries (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      file_path TEXT NOT NULL UNIQUE,
      content_hash TEXT NOT NULL,
      size_bytes INTEGER NOT NULL,
      pages_count INTEGER,
      entries_count INTEGER,
      total_bytes INTEGER,
      total_duration_ms INTEGER,
      created_at TEXT NOT NULL,
      modified_at TEXT NOT NULL,
      raw_har_json TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS shell_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      file_path TEXT NOT NULL UNIQUE,
      content_hash TEXT NOT NULL,
      size_bytes INTEGER NOT NULL,
      source TEXT,
      session_id TEXT,
      created_at TEXT NOT NULL,
      modified_at TEXT NOT NULL,
      log_text TEXT
    );
    """,
]

IDX = [
    "CREATE INDEX IF NOT EXISTS idx_docs_path ON documentation_assets(doc_path);",
    "CREATE INDEX IF NOT EXISTS idx_docs_hash ON documentation_assets(content_hash);",
    "CREATE INDEX IF NOT EXISTS idx_template_hash ON template_assets(content_hash);",
    "CREATE INDEX IF NOT EXISTS idx_har_hash ON har_entries(content_hash);",
    "CREATE INDEX IF NOT EXISTS idx_har_created ON har_entries(created_at);",
    "CREATE INDEX IF NOT EXISTS idx_shell_hash ON shell_logs(content_hash);",
    "CREATE INDEX IF NOT EXISTS idx_shell_session ON shell_logs(session_id);",
]


def ensure_enterprise_schema(db: Path = ENTERPRISE_DB) -> None:
    conn = sqlite3.connect(str(db))
    try:
        with conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            for ddl in SCHEMA:
                conn.execute(ddl)
            for idx in IDX:
                conn.execute(idx)
    finally:
        conn.close()

if __name__ == "__main__":
    ensure_enterprise_schema()
'''

run_migrations_py = r'''#!/usr/bin/env python3
from __future__ import annotations
import shutil, sqlite3, time
from pathlib import Path

BACKUP_DIR = Path("backups/db")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def snapshot(db: Path) -> Path:
    ts = time.strftime("%Y%m%d-%H%M%S")
    dest = BACKUP_DIR / f"{db.name}.bak.{ts}.sqlite"
    if db.exists():
        shutil.copy2(db, dest)
    return dest

def wal_checkpoint_truncate(conn: sqlite3.Connection) -> None:
    with conn:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")

def apply_migrations(db: Path, mig_dir: Path) -> None:
    conn = sqlite3.connect(str(db))
    try:
        with conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
        snapshot(db)
        wal_checkpoint_truncate(conn)
        for sql_file in sorted(mig_dir.glob("*.sql")):
            sql = sql_file.read_text(encoding="utf-8")
            with conn:
                conn.executescript(sql)
            print(f"applied: {sql_file}")
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    db = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("enterprise_assets.db")
    mig = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("databases/migrations")
    apply_migrations(db, mig)
'''

template_ingestor_py = r'''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Sequence

from scripts.database.lib.asset_ingestor_base import AssetIngestorBase


class TemplateAssetIngestor(AssetIngestorBase):
    kind = "template"
    patterns: Sequence[str] = ("**/*.md", "**/*.tmpl", "**/*.jinja", "**/*.j2")

    def table_name(self) -> str:
        return "template_assets"

    def schema_sql(self):
        return (
            """
            CREATE TABLE IF NOT EXISTS template_assets (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              template_path TEXT NOT NULL,
              content_hash TEXT NOT NULL,
              size_bytes INTEGER NOT NULL,
              created_at TEXT NOT NULL,
              modified_at TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS pattern_assets (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              template_path TEXT NOT NULL,
              snippet TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            """,
            "CREATE INDEX IF NOT EXISTS idx_template_hash ON template_assets(content_hash);",
        )

    def unique_predicate(self) -> str:
        return "content_hash = :content_hash"

    def _utc_now(self) -> str:
        import time
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def row_for(self, file_path: str, content_hash: str, stat: os.stat_result) -> dict:
        rel = str(Path(file_path).relative_to(self.root_dir)).replace(os.sep, "/")
        ts = self._utc_now()
        return {
            "template_path": rel,
            "content_hash": content_hash,
            "size_bytes": int(stat.st_size),
            "created_at": ts,
            "modified_at": ts,
        }

    def on_after_insert(self, row_id: int, file_path: str, row: dict) -> None:
        try:
            text = Path(file_path).read_text(encoding="utf-8")
        except Exception:
            return
        snippet = text[:1000]
        with self._connect(self.db_path) as conn:
            with conn:
                conn.execute(
                    "INSERT INTO pattern_assets(template_path, snippet, created_at) VALUES(?,?,?)",
                    (row["template_path"], snippet, row["created_at"]),
                )


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest code/document templates into enterprise_assets.db")
    ap.add_argument("--root", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--analytics")
    ap.add_argument("--batch-size", type=int, default=200)
    ns = ap.parse_args()

    ing = TemplateAssetIngestor(
        root_dir=Path(ns.root),
        db_path=Path(ns.db),
        analytics_db_path=Path(ns.analytics) if ns.analytics else None,
        batch_size=ns.batch_size,
    )
    summary = ing.ingest()
    print(summary.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

db_utils_py = r'''#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import sqlite3
from pathlib import Path

DEFAULT_BUSY_TIMEOUT_MS = 10_000


def connect_wal(path: Path, busy_timeout_ms: int = DEFAULT_BUSY_TIMEOUT_MS) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    with conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(f"PRAGMA busy_timeout={int(busy_timeout_ms)};")
        conn.execute("PRAGMA foreign_keys=ON;")
    conn.row_factory = sqlite3.Row
    return conn


@contextlib.contextmanager
def transaction(conn: sqlite3.Connection):
    with conn:
        yield conn


def wal_checkpoint_truncate(conn: sqlite3.Connection) -> None:
    with conn:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")


def integrity_check(conn: sqlite3.Connection) -> bool:
    cur = conn.execute("PRAGMA quick_check")
    row = cur.fetchone()
    return bool(row and row[0] == "ok")
'''

tests_base = r'''# tests/test_asset_ingestor_base.py
from pathlib import Path
import sqlite3

from scripts.database.lib.asset_ingestor_base import AssetIngestorBase


class DummyIngestor(AssetIngestorBase):
    kind = "dummy"
    patterns = ("**/*.txt",)

    def table_name(self) -> str:
        return "dummy_assets"

    def schema_sql(self):
        return (
            """
            CREATE TABLE IF NOT EXISTS dummy_assets (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              file_path TEXT NOT NULL UNIQUE,
              content_hash TEXT NOT NULL,
              size_bytes INTEGER NOT NULL,
              created_at TEXT NOT NULL,
              modified_at TEXT NOT NULL
            );
            """,
        )

    def unique_predicate(self) -> str:
        return "file_path = :file_path"

    def _utc_now(self) -> str:
        import time
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def row_for(self, file_path: str, content_hash: str, st):
        ts = self._utc_now()
        return {
            "file_path": file_path,
            "content_hash": content_hash,
            "size_bytes": int(st.st_size),
            "created_at": ts,
            "modified_at": ts,
        }


def test_base_ingestor_idempotent(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "a.txt").write_text("A")
    (root / "b.txt").write_text("B")

    db = tmp_path / "ent.db"
    an = tmp_path / "analytics.db"

    ing = DummyIngestor(root, db, an, batch_size=1)
    s1 = ing.ingest()
    assert s1.inserted == 2
    s2 = ing.ingest()
    assert s2.inserted == 0

    con = sqlite3.connect(str(an))
    cur = con.execute("SELECT COUNT(*) FROM event_log")
    assert cur.fetchone()[0] >= 1
    con.close()
'''

tests_docs_version = r'''# tests/test_docs_versioning.py
from pathlib import Path
from scripts.database.documentation_ingestor import DocumentationIngestor

def test_docs_versioning(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    f = docs / "note.md"
    f.write_text("v1")
    db = tmp_path / "ent.db"

    ing = DocumentationIngestor(docs, db, None, versioning=True)
    s1 = ing.ingest()
    assert s1.inserted == 1

    f.write_text("v2")
    s2 = ing.ingest()
    assert s2.inserted == 1

    import sqlite3
    con = sqlite3.connect(str(db))
    cur = con.execute("SELECT COUNT(*) FROM documentation_assets WHERE doc_path='note.md'")
    assert cur.fetchone()[0] == 2
    con.close()
'''

tests_har_logs = r'''# tests/test_har_and_logs_ingest.py
from pathlib import Path
from scripts.database.har_asset_ingestor import HarAssetIngestor
from scripts.database.shell_log_ingestor import ShellLogIngestor

def test_har_and_logs(tmp_path: Path):
    har_root = tmp_path / "har"; har_root.mkdir()
    logs_root = tmp_path / "logs"; logs_root.mkdir()

    har_file = har_root / "sample.har"
    har_file.write_text('{"log":{"pages":[],"entries":[{"startedDateTime":"2021-01-01T00:00:00Z","time":12,"response":{"bodySize":10}}]}}')

    log_file = logs_root / "cli__session_20240101-1200.log"
    log_file.write_text("line1\nline2\n")

    db = tmp_path / "ent.db"

    HarAssetIngestor(har_root, db).ingest()
    ShellLogIngestor(logs_root, db).ingest()

    import sqlite3
    con = sqlite3.connect(str(db))
    assert con.execute("SELECT COUNT(*) FROM har_entries").fetchone()[0] == 1
    assert con.execute("SELECT COUNT(*) FROM shell_logs").fetchone()[0] == 1
    con.close()
'''

tests_wal = r'''# tests/test_sqlite_wal_concurrency.py
from pathlib import Path
import threading, time
from scripts.database.lib.db_utils import connect_wal

def test_wal_read_write_concurrency(tmp_path: Path):
    db = tmp_path / "wal.db"
    con = connect_wal(db)
    with con:
        con.execute("CREATE TABLE t(id INTEGER PRIMARY KEY, v TEXT)")
    con.close()

    stop = False

    def writer():
        from scripts.database.lib.db_utils import connect_wal as cw
        c = cw(db)
        i = 0
        while not stop:
            with c:
                c.execute("INSERT INTO t(v) VALUES(?)", (f"x{i}",))
            i += 1
            time.sleep(0.005)
        c.close()

    def reader():
        from scripts.database.lib.db_utils import connect_wal as cw
        c = cw(db)
        for _ in range(50):
            c.execute("SELECT COUNT(*) FROM t").fetchone()
            time.sleep(0.005)
        c.close()

    tw = threading.Thread(target=writer)
    tr = threading.Thread(target=reader)
    tw.start(); tr.start()
    time.sleep(0.5)
    stop = True
    tw.join(); tr.join()

    assert True
'''

consistency_auditor_py = r'''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from scripts.database.lib.db_utils import connect_wal


@dataclass
class AuditCounts:
    db_to_fs_missing: int = 0
    db_to_fs_hash_mismatch: int = 0
    fs_to_db_missing: int = 0
    fixed: int = 0


@dataclass
class AuditReport:
    ok: bool
    counts: AuditCounts
    details: Dict[str, List[dict]] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({"ok": self.ok, "counts": asdict(self.counts), "details": self.details}, indent=2)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def audit(
    enterprise_db: Path,
    docs_root: Optional[Path],
    templates_root: Optional[Path],
    har_root: Optional[Path],
    logs_root: Optional[Path],
    autofix: bool = False,
) -> AuditReport:
    con = connect_wal(enterprise_db)
    counts = AuditCounts()
    details: Dict[str, List[dict]] = {"db_to_fs_missing": [], "db_to_fs_hash_mismatch": [], "fs_to_db_missing": []}

    def db_iter(sql: str, col_path: str = "file_path"):
        for row in con.execute(sql):
            yield Path(row[col_path]), row["content_hash"]

    # DB → FS checks
    for p, ch in db_iter("SELECT doc_path AS file_path, content_hash FROM v_documentation_assets_latest"):
        fp = (docs_root / p) if docs_root else p
        if not fp.exists():
            counts.db_to_fs_missing += 1
            details["db_to_fs_missing"].append({"kind": "doc", "path": str(fp)})
        else:
            if sha256_file(fp) != ch:
                counts.db_to_fs_hash_mismatch += 1
                details["db_to_fs_hash_mismatch"].append({"kind": "doc", "path": str(fp)})

    for p, ch in db_iter("SELECT template_path AS file_path, content_hash FROM template_assets"):
        fp = (templates_root / p) if templates_root else p
        if not fp.exists():
            counts.db_to_fs_missing += 1
            details["db_to_fs_missing"].append({"kind": "template", "path": str(fp)})
        else:
            if sha256_file(fp) != ch:
                counts.db_to_fs_hash_mismatch += 1
                details["db_to_fs_hash_mismatch"].append({"kind": "template", "path": str(fp)})

    for p, ch in db_iter("SELECT file_path, content_hash FROM har_entries"):
        fp = (har_root / p) if har_root and not Path(p).is_absolute() else Path(p)
        if not fp.exists():
            counts.db_to_fs_missing += 1
            details["db_to_fs_missing"].append({"kind": "har", "path": str(fp)})

    for p, ch in db_iter("SELECT file_path, content_hash FROM shell_logs"):
        fp = (logs_root / p) if logs_root and not Path(p).is_absolute() else Path(p)
        if not fp.exists():
            counts.db_to_fs_missing += 1
            details["db_to_fs_missing"].append({"kind": "log", "path": str(fp)})

    # FS → DB checks (for configured roots)
    def scan_missing(root: Optional[Path], pattern: str, table: str, key: str):
        if not root:
            return
        for p in root.rglob(pattern):
            rel = str(p.relative_to(root)).replace("\\", "/")
            row = con.execute(f"SELECT 1 FROM {table} WHERE {key}=?", (rel,)).fetchone()
            if not row:
                counts.fs_to_db_missing += 1
                details["fs_to_db_missing"].append({"kind": table, "path": rel})

    scan_missing(docs_root, "**/*.md", "documentation_assets", "doc_path")
    scan_missing(templates_root, "**/*", "template_assets", "template_path")
    scan_missing(har_root, "**/*.har", "har_entries", "file_path")
    scan_missing(logs_root, "**/*", "shell_logs", "file_path")

    con.close()
    ok = counts.db_to_fs_missing == 0 and counts.db_to_fs_hash_mismatch == 0 and (not autofix)
    return AuditReport(ok=ok, counts=counts, details=details)


def main() -> int:
    ap = argparse.ArgumentParser(description="DB↔FS consistency auditor for enterprise assets")
    ap.add_argument("--db", default="enterprise_assets.db")
    ap.add_argument("--docs-root")
    ap.add_argument("--templates-root")
    ap.add_argument("--har-root")
    ap.add_argument("--logs-root")
    ap.add_argument("--autofix", action="store_true")
    ns = ap.parse_args()

    report = audit(
        enterprise_db=Path(ns.db),
        docs_root=Path(ns.docs_root) if ns.docs_root else None,
        templates_root=Path(ns.templates_root) if ns.templates_root else None,
        har_root=Path(ns.har_root) if ns.har_root else None,
        logs_root=Path(ns.logs_root) if ns.logs_root else None,
        autofix=ns.autofix,
    )
    print(report.to_json())
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''

analytics_py = r'''#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

from scripts.database.lib.db_utils import connect_wal

class Analytics:
    """Normalized analytics/event logging for the toolkit.

    Schema (auto-created):
      event_log(id INTEGER PK, ts TEXT, kind TEXT, payload TEXT)
    """
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self._ensure()

    def _ensure(self) -> None:
        con = connect_wal(self.db_path)
        try:
            with con:
                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS event_log (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      ts TEXT NOT NULL,
                      kind TEXT NOT NULL,
                      payload TEXT NOT NULL
                    );
                    """
                )
        finally:
            con.close()

    def log(self, kind: str, payload: Dict[str, Any]) -> None:
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        con = connect_wal(self.db_path)
        try:
            with con:
                con.execute(
                    "INSERT INTO event_log(ts, kind, payload) VALUES(?,?,?)",
                    (ts, kind, json.dumps(payload, ensure_ascii=False)),
                )
        finally:
            con.close()
'''

backup_restore_py = r'''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import time
from pathlib import Path

DEFAULT_BACKUP_DIR = Path("backups/db")

def snapshot(db_path: Path, dest_dir: Path = DEFAULT_BACKUP_DIR) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    snap = dest_dir / f"{db_path.name}.bak.{ts}.sqlite"
    if db_path.exists():
        shutil.copy2(db_path, snap)
    return snap

def restore(snapshot_path: Path, db_path: Path, overwrite: bool = False) -> None:
    if db_path.exists() and not overwrite:
        raise FileExistsError(f"Target exists: {db_path}. Use --yes to overwrite.")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(snapshot_path, db_path)

def main() -> int:
    ap = argparse.ArgumentParser(description="DB snapshot/restore helper")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("snapshot")
    s1.add_argument("db")
    s1.add_argument("--dest", default=str(DEFAULT_BACKUP_DIR))

    s2 = sub.add_parser("restore")
    s2.add_argument("snap")
    s2.add_argument("--db", required=True)
    s2.add_argument("--yes", action="store_true")

    ns = ap.parse_args()

    if ns.cmd == "snapshot":
        snap = snapshot(Path(ns.db), Path(ns.dest))
        print(str(snap))
        return 0
    if ns.cmd == "restore":
        restore(Path(ns.snap), Path(ns.db), overwrite=bool(ns.yes))
        print(f"restored {ns.snap} -> {ns.db}")
        return 0
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
'''

generate_from_templates_py = r'''#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any
import sqlite3
import time

from scripts.analytics import Analytics
from scripts.database.lib.db_utils import connect_wal

def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def generate_docs(db_enterprise: Path, out_dir: Path, analytics_db: Path | None = None) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    con = connect_wal(db_enterprise)
    count = 0
    t0 = time.time()
    rows = con.execute("SELECT doc_path, content_hash FROM v_documentation_assets_latest").fetchall()
    for r in rows:
        doc_path = r["doc_path"]
        src = Path(doc_path)
        dest = out_dir / doc_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            text = src.read_text(encoding="utf-8")
        except Exception:
            text = f"# Missing source for {doc_path}\nGenerated at {_utc_now()}\n"
        dest.write_text(text, encoding="utf-8")
        count += 1
    con.close()
    dt = int((time.time() - t0) * 1000)
    if analytics_db:
        Analytics(analytics_db).log(
            "regenerate_result", {"kind": "docs", "count": count, "out_dir": str(out_dir), "duration_ms": dt}
        )
    return {"kind": "docs", "count": count, "out_dir": str(out_dir), "duration_ms": dt}

def generate_scripts(db_production: Path, out_dir: Path, analytics_db: Path | None = None) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    con = connect_wal(db_production)
    count = 0
    t0 = time.time()
    try:
        rows = con.execute("SELECT name, body FROM code_templates").fetchall()
    except sqlite3.Error:
        rows = []
    for r in rows:
        name = r["name"]
        body = r["body"]
        dest = out_dir / f"{name}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
        count += 1
    con.close()
    dt = int((time.time() - t0) * 1000)
    if analytics_db:
        Analytics(analytics_db).log(
            "regenerate_result", {"kind": "scripts", "count": count, "out_dir": str(out_dir), "duration_ms": dt}
        )
    return {"kind": "scripts", "count": count, "out_dir": str(out_dir), "duration_ms": dt}

if __name__ == "__main__":
    print(json.dumps({"hint": "Use functions generate_docs / generate_scripts from CLI/API."}, indent=2))
'''

cli_py = r'''#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from scripts.database.documentation_ingestor import DocumentationIngestor
from scripts.database.template_asset_ingestor import TemplateAssetIngestor
from scripts.database.har_asset_ingestor import HarAssetIngestor
from scripts.database.shell_log_ingestor import ShellLogIngestor

app = typer.Typer(help="gh_COPILOT — DB-first workflows")


@app.command("ingest")
def ingest(
    docs_dir: Optional[Path] = typer.Option(None, exists=True, file_okay=False, help="Docs root to scan"),
    templates_dir: Optional[Path] = typer.Option(None, exists=True, file_okay=False, help="Templates root to scan"),
    har_dir: Optional[Path] = typer.Option(None, exists=True, file_okay=False, help="HAR root to scan"),
    logs_dir: Optional[Path] = typer.Option(None, exists=True, file_okay=False, help="Logs root to scan"),
    db_enterprise: Path = typer.Option(Path("enterprise_assets.db"), help="Enterprise assets DB path"),
    db_analytics: Optional[Path] = typer.Option(Path("analytics.db"), help="Analytics DB path"),
    docs_versioning: bool = typer.Option(True, help="Enable versioning for docs"),
    update_in_place: bool = typer.Option(False, help="Update latest doc row instead of version bump"),
):
    """Ingest selected asset types into enterprise_assets.db with analytics logging."""
    results = {}
    if docs_dir:
        ing = DocumentationIngestor(
            root_dir=docs_dir,
            db_path=db_enterprise,
            analytics_db_path=db_analytics,
            versioning=docs_versioning and not update_in_place,
            update_in_place=update_in_place,
        )
        results["docs"] = json.loads(ing.ingest().to_json())
    if templates_dir:
        ing = TemplateAssetIngestor(
            root_dir=templates_dir,
            db_path=db_enterprise,
            analytics_db_path=db_analytics,
        )
        results["templates"] = json.loads(ing.ingest().to_json())
    if har_dir:
        ing = HarAssetIngestor(
            root_dir=har_dir,
            db_path=db_enterprise,
            analytics_db_path=db_analytics,
        )
        results["har"] = json.loads(ing.ingest().to_json())
    if logs_dir:
        ing = ShellLogIngestor(
            root_dir=logs_dir,
            db_path=db_enterprise,
            analytics_db_path=db_analytics,
        )
        results["logs"] = json.loads(ing.ingest().to_json())

    typer.echo(json.dumps({"ok": True, "results": results}, indent=2))


@app.command("generate")
def generate(
    kind: str = typer.Argument(..., help="docs | scripts | all"),
    out_dir: Path = typer.Option(Path("generated"), help="Output directory"),
    db_enterprise: Path = typer.Option(Path("enterprise_assets.db")),
    db_production: Path = typer.Option(Path("production.db")),
    db_analytics: Optional[Path] = typer.Option(Path("analytics.db")),
):
    """Regenerate artifacts from database templates."""
    from scripts.generate_from_templates import generate_docs, generate_scripts

    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    if kind in ("docs", "all"):
        res = generate_docs(db_enterprise=db_enterprise, out_dir=out_dir / "docs", analytics_db=db_analytics)
        results["docs"] = res
    if kind in ("scripts", "all"):
        res = generate_scripts(db_production=db_production, out_dir=out_dir / "scripts", analytics_db=db_analytics)
        results["scripts"] = res
    typer.echo(json.dumps({"ok": True, "results": results}, indent=2))


if __name__ == "__main__":
    app()
'''

api_py = r'''#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Body
from fastapi.concurrency import run_in_threadpool

from scripts.database.documentation_ingestor import DocumentationIngestor
from scripts.database.template_asset_ingestor import TemplateAssetIngestor
from scripts.database.har_asset_ingestor import HarAssetIngestor
from scripts.database.shell_log_ingestor import ShellLogIngestor
from scripts.generate_from_templates import generate_docs, generate_scripts

app = FastAPI(title="gh_COPILOT API", version="0.2.0")


@app.get("/api/v1/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/v1/ingest")
async def api_ingest(payload: dict = Body(...)) -> dict:
    docs_dir = Path(payload.get("docs_dir")) if payload.get("docs_dir") else None
    templates_dir = Path(payload.get("templates_dir")) if payload.get("templates_dir") else None
    har_dir = Path(payload.get("har_dir")) if payload.get("har_dir") else None
    logs_dir = Path(payload.get("logs_dir")) if payload.get("logs_dir") else None
    db_enterprise = Path(payload.get("db_enterprise", "enterprise_assets.db"))
    db_analytics = Path(payload.get("db_analytics", "analytics.db")) if payload.get("db_analytics") else None
    docs_versioning = bool(payload.get("docs_versioning", True))
    update_in_place = bool(payload.get("update_in_place", False))

    results = {}
    if docs_dir:
        ing = DocumentationIngestor(
            root_dir=docs_dir,
            db_path=db_enterprise,
            analytics_db_path=db_analytics,
            versioning=docs_versioning and not update_in_place,
            update_in_place=update_in_place,
        )
        results["docs"] = (await run_in_threadpool(lambda: ing.ingest().to_json()))
    if templates_dir:
        ing = TemplateAssetIngestor(
            root_dir=templates_dir,
            db_path=db_enterprise,
            analytics_db_path=db_analytics,
        )
        results["templates"] = (await run_in_threadpool(lambda: ing.ingest().to_json()))
    if har_dir:
        ing = HarAssetIngestor(
            root_dir=har_dir,
            db_path=db_enterprise,
            analytics_db_path=db_analytics,
        )
        results["har"] = (await run_in_threadpool(lambda: ing.ingest().to_json()))
    if logs_dir:
        ing = ShellLogIngestor(
            root_dir=logs_dir,
            db_path=db_enterprise,
            analytics_db_path=db_analytics,
        )
        results["logs"] = (await run_in_threadpool(lambda: ing.ingest().to_json()))

    return {"ok": True, "results": results}


@app.post("/api/v1/regenerate/{kind}")
async def api_regenerate(kind: str, payload: dict = Body({})) -> dict:
    out_dir = Path(payload.get("out_dir", "generated"))
    db_enterprise = Path(payload.get("db_enterprise", "enterprise_assets.db"))
    db_production = Path(payload.get("db_production", "production.db"))
    db_analytics = Path(payload.get("db_analytics", "analytics.db")) if payload.get("db_analytics") else None

    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    if kind in ("docs", "all"):
        results["docs"] = await run_in_threadpool(lambda: generate_docs(db_enterprise, out_dir / "docs", db_analytics))
    if kind in ("scripts", "all"):
        results["scripts"] = await run_in_threadpool(lambda: generate_scripts(db_production, out_dir / "scripts", db_analytics))
    return {"ok": True, "results": results}
'''

workflow_yml = r'''name: DB-First CI

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  test-dbfirst:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt || true
          pip install pytest tqdm fastapi typer

      - name: Run unit tests
        run: |
          pytest -q

      - name: Auditor (read-only)
        run: |
          python scripts/database/consistency_auditor.py --db enterprise_assets.db \
            --docs-root documentation --templates-root prompts --har-root har --logs-root logs || true
'''

docs_md = r'''# Database-First Workflows

This repo treats the SQLite databases as the **source of truth** for documentation, templates, HARs, and shell logs.

## Key Commands

Ingest assets into `enterprise_assets.db`:

```bash
gh-copilot ingest \
  --docs-dir documentation \
  --templates-dir prompts \
  --har-dir har \
  --logs-dir logs \
  --db-enterprise enterprise_assets.db \
  --db-analytics analytics.db
Regenerate artifacts from DB templates:

bash
Always show details

Copy
gh-copilot generate docs --out-dir generated --db-enterprise enterprise_assets.db
gh-copilot generate scripts --out-dir generated --db-production production.db
Audit DB↔FS consistency:

bash
Always show details

Copy
python scripts/database/consistency_auditor.py \
  --db enterprise_assets.db \
  --docs-root documentation \
  --templates-root prompts \
  --har-root har \
  --logs-root logs
'''

gitattributes = r'''# Git LFS rules for ZIP and other common archives

*.[zZ][iI][pP] filter=lfs diff=lfs merge=lfs -text
*.tar filter=lfs diff=lfs merge=lfs -text
*.tgz filter=lfs diff=lfs merge=lfs -text # tar.gz
*.tar.gz filter=lfs diff=lfs merge=lfs -text
*.tbz2 filter=lfs diff=lfs merge=lfs -text # tar.bz2
*.tar.bz2 filter=lfs diff=lfs merge=lfs -text
*.txz filter=lfs diff=lfs merge=lfs -text # tar.xz
*.tar.xz filter=lfs diff=lfs merge=lfs -text
*.tzst filter=lfs diff=lfs merge=lfs -text # tar.zst
*.tar.zst filter=lfs diff=lfs merge=lfs -text

*.7z filter=lfs diff=lfs merge=lfs -text
*.rar filter=lfs diff=lfs merge=lfs -text
*.jar filter=lfs diff=lfs merge=lfs -text
*.war filter=lfs diff=lfs merge=lfs -text
*.ear filter=lfs diff=lfs merge=lfs -text
*.apk filter=lfs diff=lfs merge=lfs -text
*.ipa filter=lfs diff=lfs merge=lfs -text
*.nupkg filter=lfs diff=lfs merge=lfs -text
*.cab filter=lfs diff=lfs merge=lfs -text
*.iso filter=lfs diff=lfs merge=lfs -text
'''

pre_commit_config = r'''repos:

repo: https://github.com/pre-commit/pre-commit-hooks
rev: v4.6.0
hooks:

id: check-added-large-files
args: ["--maxkb=100"]

repo: local
hooks:

id: enforce-lfs-for-archives
name: enforce-lfs-for-archives
entry: bash -c '
set -euo pipefail;
PATTERN=".(zip|jar|war|ear|7z|rar|tar|tgz|tar.gz|tbz2|tar.bz2|txz|tar.xz|tzst|tar.zst|apk|ipa|nupkg|cab|iso)$";
files=$(git diff --cached --name-only | grep -Ei "$PATTERN" || true);
if [ -z "$files" ]; then exit 0; fi;
failed=0;
for f in $files; do
attr=$(git check-attr filter -- "$f" | awk -F: "{print $3}" | xargs);
if [ "$attr" != "lfs" ]; then
echo "ERROR: $f is an archive but not tracked by Git LFS. Add a rule to .gitattributes and re-stage." >&2;
failed=1;
fi;
done;
exit $failed
'
language: system
files: ".(zip|jar|war|ear|7z|rar|tar|tgz|tar.gz|tbz2|tar.bz2|txz|tar.xz|tzst|tar.zst|apk|ipa|nupkg|cab|iso)$"

id: forbid-untracked-generated
name: forbid-edits-to-generated
entry: bash -c '
set -euo pipefail;
if [ -d generated ]; then
changed=$(git diff --cached --name-only -- generated || true);
if [ -n "$changed" ]; then
echo "ERROR: Edits under ./generated/ must be produced by the generator, not manual changes." >&2;
exit 1;
fi;
fi'
language: system
files: "^generated/"
'''

bootstrap_lfs_precommit_sh = r'''#!/usr/bin/env bash
set -euo pipefail

: "${DRY_RUN:=}"
: "${BOOTSTRAP_NO_RUN:=}"
: "${FORCE_COMMIT:=}"

run(){ if [[ -n "${DRY_RUN}" ]]; then echo "[DRY] $@"; else eval "$@"; fi; }

ensure_gitattributes() {
if [[ ! -f .gitattributes ]]; then
cat > .gitattributes <<'ATTR'
*.[zZ][iI][pP] filter=lfs diff=lfs merge=lfs -text
*.tar filter=lfs diff=lfs merge=lfs -text
*.tgz filter=lfs diff=lfs merge=lfs -text
*.tar.gz filter=lfs diff=lfs merge=lfs -text
*.tbz2 filter=lfs diff=lfs merge=lfs -text
*.tar.bz2 filter=lfs diff=lfs merge=lfs -text
*.txz filter=lfs diff=lfs merge=lfs -text
*.tar.xz filter=lfs diff=lfs merge=lfs -text
*.tzst filter=lfs diff=lfs merge=lfs -text
*.tar.zst filter=lfs diff=lfs merge=lfs -text
*.7z filter=lfs diff=lfs merge=lfs -text
*.rar filter=lfs diff=lfs merge=lfs -text
*.jar filter=lfs diff=lfs merge=lfs -text
*.war filter=lfs diff=lfs merge=lfs -text
*.ear filter=lfs diff=lfs merge=lfs -text
*.apk filter=lfs diff=lfs merge=lfs -text
*.ipa filter=lfs diff=lfs merge=lfs -text
*.nupkg filter=lfs diff=lfs merge=lfs -text
*.cab filter=lfs diff=lfs merge=lfs -text
*.iso filter=lfs diff=lfs merge=lfs -text
ATTR
run "git add .gitattributes"
fi
}

main(){
run "git lfs install"
ensure_gitattributes
if [[ ! -f .pre-commit-config.yaml ]]; then
cat > .pre-commit-config.yaml <<'PC'
repos:

repo: https://github.com/pre-commit/pre-commit-hooks
rev: v4.6.0
hooks:

id: check-added-large-files
args: ["--maxkb=100"]

repo: local
hooks:

id: enforce-lfs-for-archives
name: enforce-lfs-for-archives
entry: bash -c '
set -euo pipefail;
PATTERN=".(zip|jar|war|ear|7z|rar|tar|tgz|tar.gz|tbz2|tar.bz2|txz|tar.xz|tzst|tar.zst|apk|ipa|nupkg|cab|iso)$";
files=$(git diff --cached --name-only | grep -Ei "$PATTERN" || true);
if [ -z "$files" ]; then exit 0; fi;
failed=0;
for f in $files; do
attr=$(git check-attr filter -- "$f" | awk -F: "{print $3}" | xargs);
if [ "$attr" != "lfs" ]; then
echo "ERROR: $f is an archive but not tracked by Git LFS. Fix .gitattributes and re-stage." >&2;
failed=1;
fi;
done;
exit $failed
'
language: system
files: ".(zip|jar|war|ear|7z|rar|tar|tgz|tar.gz|tbz2|tar.bz2|txz|tar.xz|tzst|tar.zst|apk|ipa|nupkg|cab|iso)$"
PC
run "git add .pre-commit-config.yaml"
fi
run "pre-commit install"
run "pre-commit install --hook-type pre-push"
if [[ -z "${BOOTSTRAP_NO_RUN}" ]]; then
run "pre-commit run --all-files" || true
fi
if [[ -n "${FORCE_COMMIT}" ]]; then
run "git commit -m 'chore: bootstrap LFS + pre-commit' || true"
fi
echo "✅ Bootstrap complete"
}

main "$@"
'''

lfs_guard_yml = r'''name: LFS Guard

on:
  pull_request:

jobs:
  enforce-lfs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          lfs: true
          fetch-depth: 0

      - name: Enforce LFS for archive files
        run: |
          set -euo pipefail
          git fetch origin "$GITHUB_BASE_REF" --depth=1
          git diff --name-only --diff-filter=AM origin/"$GITHUB_BASE_REF"...HEAD > changed_files.txt
          archives=$(grep -E '\\.(zip|jar|tar.*|7z|rar|apk|ipa|nupkg|cab|iso)$' changed_files.txt || true)
          if [[ -z "$archives" ]]; then
            echo "No archive files added or modified."
            exit 0
          fi
          missing_files=""
          while IFS= read -r file; do
            if ! git check-attr filter -- "$file" | grep -q 'filter: lfs'; then
              echo "::error file=$file::Archive file is not tracked by Git LFS"
              missing_files+="$file\n"
            fi
          done <<< "$archives"
          if [[ -n "$missing_files" ]]; then
            echo -e "The following archive files are not tracked by Git LFS:\n$missing_files"
            exit 1
          fi
          echo "All archive files are properly tracked by Git LFS."
'''

circleci_config = r'''version: 2.1
jobs:
verify-lfs:
docker:
- image: cimg/base:stable
steps:
- checkout
- run:
name: Install Git LFS
command: |
sudo apt-get update -y
sudo apt-get install -y git-lfs
git lfs install
- run:
name: Verify archives tracked by LFS
command: |
set -euo pipefail
PATTERN='.(zip|jar|war|ear|7z|rar|tar|tgz|tar.gz|tbz2|tar.bz2|txz|tar.xz|tzst|tar.zst|apk|ipa|nupkg|cab|iso)$'
changed=$(git diff --name-only HEAD~1 | grep -Ei "$PATTERN" || true)
if [ -z "$changed" ]; then echo "No archives changed"; exit 0; fi
echo "Changed archives:"
echo "$changed"
failed=0
while read -r f; do
[ -z "$f" ] && continue
attr=$(git check-attr filter -- "$f" | awk -F: '{print $3}' | xargs)
if [ "$attr" != "lfs" ]; then
echo "FAIL: $f is an archive and MUST be tracked by Git LFS."
failed=1
fi
done <<< "$changed"
exit $failed
workflows:
verify:
jobs:
- verify-lfs
'''

pre_commit_hook = r'''#!/usr/bin/env bash

hooks/pre-commit — enforce LFS for archives and prevent manual edits under generated/
set -euo pipefail

PATTERN='.(zip|jar|war|ear|7z|rar|tar|tgz|tar.gz|tbz2|tar.bz2|txz|tar.xz|tzst|tar.zst|apk|ipa|nupkg|cab|iso)$'

1) Enforce LFS for archives
files=$(git diff --cached --name-only | grep -Ei "$PATTERN" || true)
if [ -n "$files" ]; then
fail=0
while read -r f; do
[ -z "$f" ] && continue
attr=$(git check-attr filter -- "$f" | awk -F: '{print $3}' | xargs)
if [ "$attr" != "lfs" ]; then
echo "ERROR: $f is an archive but not tracked by Git LFS. Update .gitattributes and re-stage." >&2
fail=1
fi
done <<< "$files"
[ $fail -eq 0 ] || exit 1
fi

2) Prevent manual edits under generated/
changed=$(git diff --cached --name-only -- generated || true)
if [ -n "$changed" ]; then
echo "ERROR: Edits under ./generated/ are not allowed; regenerate via CLI/API." >&2
exit 1
fi
'''

makefile_unix = r'''# Makefile — DB-first happy path
SHELL := /bin/bash
PY ?= python3
PIP ?= pip3

SRC_DIR := src
export PYTHONPATH := $(PWD)/$(SRC_DIR)

DB_ENTERPRISE ?= enterprise_assets.db
DB_ANALYTICS ?= analytics.db
DB_PRODUCTION ?= production.db

DOCS_DIR ?= documentation
TEMPLATES_DIR ?= prompts
HAR_DIR ?= har
LOGS_DIR ?= logs
OUT_DIR ?= generated

MIG_DIR ?= databases/migrations

.DEFAULT_GOAL := all

.PHONY: all deps init migrate ingest generate audit test ci-check clean help

help:
@echo "Targets:"
@echo " make migrate # apply migrations to $(DB_ENTERPRISE)"
@echo " make ingest # ingest docs/templates/HAR/logs into $(DB_ENTERPRISE)"
@echo " make generate # regenerate docs+scripts into $(OUT_DIR)"
@echo " make audit # DB<->FS integrity audit"
@echo " make test # run tests"
@echo " make all # migrate ingest generate audit test"

deps:
$(PIP) install --upgrade pip >/dev/null 2>&1 || true
$(PIP) install -r requirements.txt >/dev/null 2>&1 || true
$(PIP) install pytest fastapi typer tqdm >/dev/null 2>&1

init:
$(PY) scripts/database/unified_database_initializer.py

migrate: deps
$(PY) scripts/database/run_migrations.py $(DB_ENTERPRISE) $(MIG_DIR)
@echo "✅ Migration complete for $(DB_ENTERPRISE)"

ingest: deps
$(PY) -m gh_copilot.cli ingest
--docs-dir $(DOCS_DIR)
--templates-dir $(TEMPLATES_DIR)
--har-dir $(HAR_DIR)
--logs-dir $(LOGS_DIR)
--db-enterprise $(DB_ENTERPRISE)
--db-analytics $(DB_ANALYTICS)

generate: deps
$(PY) -m gh_copilot.cli generate all
--out-dir $(OUT_DIR)
--db-enterprise $(DB_ENTERPRISE)
--db-production $(DB_PRODUCTION)
--db-analytics $(DB_ANALYTICS)

audit:
$(PY) scripts/database/consistency_auditor.py
--db $(DB_ENTERPRISE)
--docs-root $(DOCS_DIR)
--templates-root $(TEMPLATES_DIR)
--har-root $(HAR_DIR)
--logs-root $(LOGS_DIR)

test: deps
pytest -q

all: migrate ingest generate audit test

ci-check: migrate test audit

clean:
rm -rf $(OUT_DIR) pycache .pytest_cache **/pycache
'''

taskfile_yml = r'''version: '3'

env:
PYTHONPATH: '{{.USER_WORKING_DIR}}/src'
PY: python3
PIP: pip3

vars:
DB_ENTERPRISE: enterprise_assets.db
DB_ANALYTICS: analytics.db
DB_PRODUCTION: production.db

DOCS_DIR: documentation
TEMPLATES_DIR: prompts
HAR_DIR: har
LOGS_DIR: logs
OUT_DIR: generated

MIG_DIR: databases/migrations

tasks:
default:
deps: [migrate, ingest, generate, audit, test]
cmds:
- echo "✅ DB-first happy path complete"

deps:
cmds:
- '{{.PIP}} install --upgrade pip || true'
- '{{.PIP}} install -r requirements.txt || true'
- '{{.PIP}} install pytest fastapi typer tqdm'

migrate:
deps: [deps]
cmds:
- '{{.PY}} scripts/database/run_migrations.py {{.DB_ENTERPRISE}} {{.MIG_DIR}}'
- echo '✅ Migration complete for {{.DB_ENTERPRISE}}'

ingest:
deps: [deps]
cmds:
- >-
{{.PY}} -m gh_copilot.cli ingest
--docs-dir {{.DOCS_DIR}}
--templates-dir {{.TEMPLATES_DIR}}
--har-dir {{.HAR_DIR}}
--logs-dir {{.LOGS_DIR}}
--db-enterprise {{.DB_ENTERPRISE}}
--db-analytics {{.DB_ANALYTICS}}

generate:
deps: [deps]
cmds:
- >-
{{.PY}} -m gh_copilot.cli generate all
--out-dir {{.OUT_DIR}}
--db-enterprise {{.DB_ENTERPRISE}}
--db-production {{.DB_PRODUCTION}}
--db-analytics {{.DB_ANALYTICS}}

audit:
cmds:
- >-
{{.PY}} scripts/database/consistency_auditor.py
--db {{.DB_ENTERPRISE}}
--docs-root {{.DOCS_DIR}}
--templates-root {{.TEMPLATES_DIR}}
--har-root {{.HAR_DIR}}
--logs-root {{.LOGS_DIR}}

test:
deps: [deps]
cmds:
- pytest -q

clean:
cmds:
- rm -rf {{.OUT_DIR}} pycache .pytest_cache **/pycache
'''

makefile_win = r'''# Makefile.win — DB-first happy path for Windows (PowerShell-backed)
SHELL := cmd
POWERSHELL := powershell -NoProfile -ExecutionPolicy Bypass -Command
PY := python

DB_ENTERPRISE := enterprise_assets.db
DB_ANALYTICS := analytics.db
DB_PRODUCTION := production.db

DOCS_DIR := documentation
TEMPLATES_DIR := prompts
HAR_DIR := har
LOGS_DIR := logs
OUT_DIR := generated

MIG_DIR := databases\migrations

.DEFAULT_GOAL := all

.PHONY: all deps migrate ingest generate audit test clean help

help:
@echo Targets:
@echo make -f Makefile.win migrate ^# apply migrations to $(DB_ENTERPRISE)
@echo make -f Makefile.win ingest ^# ingest docs/templates/HAR/logs
@echo make -f Makefile.win generate ^# regenerate docs+scripts
@echo make -f Makefile.win audit ^# DB^<->FS integrity audit
@echo make -f Makefile.win test ^# run tests

deps:
$(POWERSHELL) "$(PY) -m pip install --upgrade pip ^|^| exit 0; $(PY) -m pip install -r requirements.txt ^|^| echo 'requirements.txt not found'; $(PY) -m pip install pytest fastapi typer tqdm"

migrate: deps
$(POWERSHELL) "$(PY) scripts\database\run_migrations.py '$(DB_ENTERPRISE)' '$(MIG_DIR)'; Write-Host '✅ Migration complete for $(DB_ENTERPRISE)'"

ingest: deps
$(POWERSHELL) "$(PY) -m gh_copilot.cli ingest --docs-dir '$(DOCS_DIR)' --templates-dir '$(TEMPLATES_DIR)' --har-dir '$(HAR_DIR)' --logs-dir '$(LOGS_DIR)' --db-enterprise '$(DB_ENTERPRISE)' --db-analytics '$(DB_ANALYTICS)'"

generate: deps
$(POWERSHELL) "$(PY) -m gh_copilot.cli generate all --out-dir '$(OUT_DIR)' --db-enterprise '$(DB_ENTERPRISE)' --db-production '$(DB_PRODUCTION)' --db-analytics '$(DB_ANALYTICS)'"

audit:
$(POWERSHELL) "$(PY) scripts\database\consistency_auditor.py --db '$(DB_ENTERPRISE)' --docs-root '$(DOCS_DIR)' --templates-root '$(TEMPLATES_DIR)' --har-root '$(HAR_DIR)' --logs-root '$(LOGS_DIR)'; if (LASTEXITCODE -ne 0) { exit LASTEXITCODE }"

test: deps
$(POWERSHELL) "pytest -q; if (LASTEXITCODE -ne 0) { exit LASTEXITCODE }"

all: migrate ingest generate audit test

clean:
$(POWERSHELL) "Remove-Item -Recurse -Force '$(OUT_DIR)' -ErrorAction SilentlyContinue; Get-ChildItem -Recurse -Force -Include pycache,.pytest_cache ^| Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
'''

invoke_dbfirst_ps1 = r'''<#
.SYNOPSIS
DB-first happy path for Windows (PowerShell). Wraps migrate, ingest, generate, audit, and test.
#>
param(
[ValidateSet('All','Migrate','Ingest','Generate','Audit','Test')]
[string]$Task = 'All',
[string]$DocsDir = 'documentation',
[string]$TemplatesDir = 'prompts',
[string]$HarDir = 'har',
[string]$LogsDir = 'logs',
[string]$OutDir = 'generated',
[string]$EnterpriseDb = 'enterprise_assets.db',
[string]$AnalyticsDb = 'analytics.db',
[string]$ProductionDb = 'production.db',
[switch]$DocsVersioning = $true,
[switch]$UpdateInPlace = $false
)
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$src = Join-Path $here 'src'
$env:PYTHONPATH = $src

function Ensure-Python {
try { Get-Command python -ErrorAction Stop | Out-Null }
catch { throw 'Python not found on PATH. Install Python 3 and try again.' }
}

function Invoke-Deps {
python -m pip install --upgrade pip | Out-Null
try { python -m pip install -r requirements.txt | Out-Null } catch { Write-Verbose 'requirements.txt not found; continuing' }
python -m pip install pytest fastapi typer tqdm | Out-Null
}

function Invoke-Migrate {
Write-Host '⏳ Applying migrations...' -ForegroundColor Cyan
python scripts\database\run_migrations.py $EnterpriseDb databases\migrations
Write-Host "✅ Migration complete for $EnterpriseDb" -ForegroundColor Green
}

function Invoke-Ingest {
Write-Host '⏳ Ingesting assets...' -ForegroundColor Cyan
$args = @('ingest', '--db-enterprise', $EnterpriseDb, '--db-analytics', $AnalyticsDb)
if (Test-Path $DocsDir) { $args += @('--docs-dir', $DocsDir) }
if (Test-Path $TemplatesDir) { $args += @('--templates-dir', $TemplatesDir) }
if (Test-Path $HarDir) { $args += @('--har-dir', $HarDir) }
if (Test-Path $LogsDir) { $args += @('--logs-dir', $LogsDir) }
if ($UpdateInPlace) { $args += '--in-place' } elseif (-not $DocsVersioning) { $args += '--no-versioning' }
python -m gh_copilot.cli @args
}

function Invoke-Generate {
Write-Host '⏳ Generating artifacts from DB templates...' -ForegroundColor Cyan
python -m gh_copilot.cli generate all --out-dir $OutDir --db-enterprise $EnterpriseDb --db-production $ProductionDb --db-analytics $AnalyticsDb
}

function Invoke-Audit {
Write-Host '⏳ Auditing DB↔FS consistency...' -ForegroundColor Cyan
python scripts\database\consistency_auditor.py --db $EnterpriseDb --docs-root $DocsDir --templates-root $TemplatesDir --har-root $HarDir --logs-root $LogsDir
}

function Invoke-Test {
Write-Host '⏳ Running tests...' -ForegroundColor Cyan
pytest -q
}

function Invoke-All { Invoke-Migrate; Invoke-Ingest; Invoke-Generate; Invoke-Audit; Invoke-Test }

Ensure-Python
Invoke-Deps

switch ($Task) {
'All' { Invoke-All }
'Migrate' { Invoke-Migrate }
'Ingest' { Invoke-Ingest }
'Generate' { Invoke-Generate }
'Audit' { Invoke-Audit }
'Test' { Invoke-Test }
}
'''

# ---------------- Write all files ----------------
write(root / "scripts/database/lib/asset_ingestor_base.py", asset_ingestor_base_py)
write(root / "scripts/database/har_asset_ingestor.py", har_asset_ingestor_py)
write(root / "scripts/database/shell_log_ingestor.py", shell_log_ingestor_py)
write(root / "scripts/database/documentation_ingestor.py", documentation_ingestor_py)
write(root / "databases/migrations/00XX_enterprise_assets_add_har_shell_and_docs_version.sql", migration_sql)
write(root / "scripts/database/unified_database_initializer.py", initializer_py)
write(root / "scripts/database/run_migrations.py", run_migrations_py)
write(root / "scripts/database/template_asset_ingestor.py", template_ingestor_py)
write(root / "scripts/database/lib/db_utils.py", db_utils_py)
write(root / "scripts/database/consistency_auditor.py", consistency_auditor_py)
write(root / "scripts/database/backup_and_restore.py", backup_restore_py)
write(root / "scripts/generate_from_templates.py", generate_from_templates_py)
write(root / "scripts/analytics.py", analytics_py)

write(root / "src/gh_copilot/cli.py", cli_py)
write(root / "src/gh_copilot/api.py", api_py)

write(root / "tests/test_asset_ingestor_base.py", tests_base)
write(root / "tests/test_docs_versioning.py", tests_docs_version)
write(root / "tests/test_har_and_logs_ingest.py", tests_har_logs)
write(root / "tests/test_sqlite_wal_concurrency.py", tests_wal)

write(root / ".github/workflows/dbfirst.yml", workflow_yml)
write(root / ".github/workflows/lfs-guard.yml", lfs_guard_yml)
write(root / ".circleci/config.yml", circleci_config)
write(root / "docs/database_first.md", docs_md)

write(root / ".gitattributes", gitattributes)
write(root / ".pre-commit-config.yaml", pre_commit_config)
write(root / "bootstrap_lfs_precommit.sh", bootstrap_lfs_precommit_sh)
write(root / "hooks/pre-commit", pre_commit_hook)

write(root / "Makefile", makefile_unix)
write(root / "Taskfile.yml", taskfile_yml)
write(root / "Makefile.win", makefile_win)
write(root / "Invoke-DbFirst.ps1", invoke_dbfirst_ps1)

# ---------------- Create the ZIP ----------------
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
for p in root.rglob("*"):
if p.is_file():
z.write(p, arcname=str(p.relative_to(root)))

print(json.dumps({"zip": str(zip_path), "files": sum(1 for _ in root.rglob('*') if _.is_file())}, indent=2))
