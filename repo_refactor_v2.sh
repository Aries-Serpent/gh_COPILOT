#!/usr/bin/env bash
set -euo pipefail
# -----------------------------------------------------------------------------
# gh_COPILOT — One‑Shot Refactor v2
# Goals (fixes your blockers):
#   ✓ Materialize scripts/generate_from_templates.py (missing wrapper)
#   ✓ OVERWRITE scripts/database/har_ingestor.py in-place (WAL + timeout + batching)
#   ✓ Provide stable ingest_har_entries entrypoint for CLI/API imports
#   ✓ Add compat migration for HAR schema (content_hash/metrics ⇄ sha256/metrics_json)
#   ✓ Ensure CLI has `migrate-all` & `generate`; wire `ingest-har` to new entrypoint
#   ✓ Seed minimal template tables (optional) so generation doesn't fail on empty DBs
#   ✓ Idempotent; use --force to overwrite anything
# -----------------------------------------------------------------------------

FORCE=${1:-}
ROOT_DIR=$(pwd)
SRC_DIR="$ROOT_DIR/src"
PKG_BASE="$SRC_DIR/gh_copilot"
INGEST_PKG="$PKG_BASE/ingest"
GEN_PKG="$PKG_BASE/generation"
MIG_DIR="$ROOT_DIR/databases/migrations"
SCRIPTS_DIR="$ROOT_DIR/scripts"
DB_DIR="$ROOT_DIR/databases"
CLI_FILE="$PKG_BASE/cli.py"
API_FILE="$PKG_BASE/api.py"

say() { printf "\033[1;34m[refactor]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[warn]\033[0m %s\n" "$*"; }
err()  { printf "\033[1;31m[err]\033[0m %s\n" "$*"; }
info() { printf "\033[0;36m[i]\033[0m %s\n" "$*"; }

mkdir -p "$GEN_PKG" "$INGEST_PKG" "$MIG_DIR" "$SCRIPTS_DIR" "$DB_DIR" "$PKG_BASE"

# -----------------------------------------------------------------------------
# 0) Minimal pyproject if missing (ensures typer etc.)
# -----------------------------------------------------------------------------
if [[ ! -f "$ROOT_DIR/pyproject.toml" ]]; then
  cat > "$ROOT_DIR/pyproject.toml" <<'PYTOML'
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "gh-copilot"
version = "0.0.5"
description = "gh_COPILOT — refactor v2 (generator wrapper + HAR overwrite + compat)"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.110",
  "uvicorn[standard]>=0.23",
  "pydantic>=2.6",
  "typer[all]>=0.12",
  "httpx>=0.27; extra == 'dev'"
]

[project.optional-dependencies]
dev = ["pytest>=8.2", "pytest-cov>=5.0", "ruff>=0.5", "mypy>=1.10"]

[project.scripts]
gh-copilot = "gh_copilot.cli:app"
PYTOML
  say "wrote: pyproject.toml"
else
  info "pyproject.toml exists — ensure it includes typer/pytest-cov in your env"
fi

# -----------------------------------------------------------------------------
# 1) scripts/generate_from_templates.py — REQUIRED by Set 3
# -----------------------------------------------------------------------------
if [[ -f "$SCRIPTS_DIR/generate_from_templates.py" && "$FORCE" != "--force" ]]; then
  info "exists: scripts/generate_from_templates.py (use --force to overwrite)"
else
  cat > "$SCRIPTS_DIR/generate_from_templates.py" <<'PY'
#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
import typer

# Ensure package import works either installed or source tree
try:
    import gh_copilot  # type: ignore
except Exception:
    here = Path(__file__).resolve()
    src = here.parents[1] / "src"
    if src.exists():
        sys.path.insert(0, str(src))
    import gh_copilot  # type: ignore

from gh_copilot.generation.generate_from_templates import generate as _generate

app = typer.Typer(help="Generate docs/scripts from DB templates and log events")

@app.command()
def main(
    kind: str = typer.Argument(..., help="docs|scripts"),
    source_db: Path = typer.Option(Path("documentation.db"), help="DB with templates"),
    out_dir: Path = typer.Option(Path("generated"), help="Output directory"),
    analytics_db: Path = typer.Option(Path("analytics.db"), help="Analytics DB"),
    params: str = typer.Option("", help="JSON substitutions e.g. '{\"project\":\"X\"}'"),
) -> None:
    values = json.loads(params) if params else {}
    written = _generate(kind=kind, source_db=source_db, out_dir=out_dir, analytics_db=analytics_db, params=values)
    print(json.dumps({"written": [str(p) for p in written]}, indent=2))

if __name__ == "__main__":
    app()
PY
  chmod +x "$SCRIPTS_DIR/generate_from_templates.py" || true
  say "wrote: scripts/generate_from_templates.py"
fi

# -----------------------------------------------------------------------------
# 2) Package generator (only create if missing)
# -----------------------------------------------------------------------------
[[ -f "$GEN_PKG/__init__.py" ]] || echo "__all__ = [\"dao\", \"generate_from_templates\"]" > "$GEN_PKG/__init__.py"
if [[ ! -f "$GEN_PKG/dao.py" ]]; then
  cat > "$GEN_PKG/dao.py" <<'PY'
from __future__ import annotations
import sqlite3, json
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

PRAGMAS = (
    "PRAGMA journal_mode=WAL;",
    "PRAGMA synchronous=NORMAL;",
    "PRAGMA foreign_keys=ON;",
    "PRAGMA busy_timeout=10000;",
)

def get_conn(db: Path) -> sqlite3.Connection:
    c = sqlite3.connect(db)
    c.row_factory = sqlite3.Row
    for p in PRAGMAS:
        c.execute(p)
    return c

class GenerationDAO:
    def __init__(self, analytics_db: Path):
        self.analytics_db = analytics_db
    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        c = get_conn(self.analytics_db)
        try:
            yield c
        finally:
            c.close()
    def log_event(self, kind: str, source: str, target_path: str, template_id: str|None, inputs: dict) -> None:
        with self._conn() as c, c:
            c.execute(
                "INSERT INTO generation_events(kind, source, target_path, template_id, inputs_json, ts) VALUES (?,?,?,?,?,?)",
                (kind, source, target_path, template_id, json.dumps(inputs), datetime.utcnow().isoformat()),
            )
PY
  say "wrote: src/gh_copilot/generation/dao.py"
fi
if [[ ! -f "$GEN_PKG/generate_from_templates.py" ]]; then
  cat > "$GEN_PKG/generate_from_templates.py" <<'PY'
from __future__ import annotations
import json, sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

from .dao import GenerationDAO

@dataclass
class TemplateRecord:
    id: str
    path: str
    content: str

def _fetch_templates(db: Path, table: str) -> List[TemplateRecord]:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(f"SELECT id, path, content FROM {table}").fetchall()
        return [TemplateRecord(id=str(r['id']), path=r['path'], content=r['content']) for r in rows]
    finally:
        conn.close()

def _render_doc(t: TemplateRecord, params: Dict[str, str]) -> str:
    out = t.content
    for k, v in params.items():
        out = out.replace(f"{{{{{k}}}}}", v)
    return out

def generate(kind: str, source_db: Path, out_dir: Path, analytics_db: Path, params: Dict[str,str]|None=None) -> list[Path]:
    params = params or {}
    dao = GenerationDAO(analytics_db)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    if kind == "docs":
        templates = _fetch_templates(source_db, table="documentation_templates")
        for t in templates:
            target = out_dir / Path(t.path).with_suffix(".md").name
            content = _render_doc(t, params)
            target.write_text(content, encoding="utf-8")
            dao.log_event(kind="docs", source=str(source_db), target_path=str(target), template_id=t.id, inputs=params)
            written.append(target)
    elif kind == "scripts":
        templates = _fetch_templates(source_db, table="script_templates")
        for t in templates:
            target = out_dir / Path(t.path).with_suffix(".py").name
            target.write_text(t.content, encoding="utf-8")
            dao.log_event(kind="scripts", source=str(source_db), target_path=str(target), template_id=t.id, inputs=params)
            written.append(target)
    else:
        raise ValueError("kind must be 'docs' or 'scripts'")
    return written
PY
  say "wrote: src/gh_copilot/generation/generate_from_templates.py"
fi

# -----------------------------------------------------------------------------
# 3) Migrations: events + HAR base + HAR compatibility (columns + backfill)
# -----------------------------------------------------------------------------
[[ -f "$MIG_DIR/0004_ingest_events.sql" ]] || cat > "$MIG_DIR/0004_ingest_events.sql" <<'SQL'
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS ingest_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,
  path TEXT NOT NULL,
  sha256 TEXT,
  content_hash TEXT,
  metrics_json TEXT,
  metrics TEXT,
  ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ingest_events_ts ON ingest_events(ts DESC);
SQL
[[ -f "$MIG_DIR/0005_generation_events.sql" ]] || cat > "$MIG_DIR/0005_generation_events.sql" <<'SQL'
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS generation_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,
  source TEXT NOT NULL,
  target_path TEXT NOT NULL,
  template_id TEXT,
  inputs_json TEXT,
  ts TEXT NOT NULL,
  status TEXT DEFAULT 'ok',
  error_message TEXT
);
CREATE INDEX IF NOT EXISTS idx_generation_events_ts ON generation_events(ts DESC);
SQL
[[ -f "$MIG_DIR/0006_har_entries.sql" ]] || cat > "$MIG_DIR/0006_har_entries.sql" <<'SQL'
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS har_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  path TEXT NOT NULL,
  sha256 TEXT,
  content_hash TEXT,
  created_at TEXT NOT NULL,
  metrics_json TEXT,
  metrics TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_har_entries_path_hash ON har_entries(path, COALESCE(sha256, content_hash));
SQL
# Compat migration adds missing columns and backfills; keeps both in sync going forward
cat > "$MIG_DIR/0007_har_schema_compat.py" <<'PY'
# Idempotent compat migration for har_entries: ensure both sha256/content_hash and metrics/metrics_json exist
import sqlite3

def _cols(conn: sqlite3.Connection, table: str) -> set[str]:
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}

def upgrade(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE TABLE IF NOT EXISTS har_entries(id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT NOT NULL, created_at TEXT NOT NULL)")
    cols = _cols(conn, "har_entries")
    if "sha256" not in cols:
        conn.execute("ALTER TABLE har_entries ADD COLUMN sha256 TEXT")
    if "content_hash" not in cols:
        conn.execute("ALTER TABLE har_entries ADD COLUMN content_hash TEXT")
    if "metrics_json" not in cols:
        conn.execute("ALTER TABLE har_entries ADD COLUMN metrics_json TEXT")
    if "metrics" not in cols:
        conn.execute("ALTER TABLE har_entries ADD COLUMN metrics TEXT")
    # Backfill: prefer sha256->content_hash if present
    conn.execute("UPDATE har_entries SET content_hash = COALESCE(content_hash, sha256)")
    # Backfill metrics: prefer metrics_json -> metrics as text if empty
    conn.execute("UPDATE har_entries SET metrics = COALESCE(metrics, metrics_json)")
    # Recreate unique index
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_har_entries_path_hash ON har_entries(path, COALESCE(sha256, content_hash))")
    conn.commit()
PY
say "wrote migrations 0004..0007"

# -----------------------------------------------------------------------------
# 4) Ingestion package: stable entrypoint used by CLI & script
# -----------------------------------------------------------------------------
cat > "$INGEST_PKG/__init__.py" <<'PY'
from .har import ingest_har_entries, IngestResult  # re-export stable entrypoints
__all__ = ["ingest_har_entries", "IngestResult"]
PY

cat > "$INGEST_PKG/har.py" <<'PY'
from __future__ import annotations
import json, sqlite3, hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

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
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS har_entries (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          path TEXT NOT NULL,
          sha256 TEXT,
          content_hash TEXT,
          created_at TEXT NOT NULL,
          metrics_json TEXT,
          metrics TEXT
        );
        CREATE UNIQUE INDEX IF NOT EXISTS ux_har_entries_path_hash ON har_entries(path, COALESCE(sha256, content_hash));
        """
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
    inserted = skipped = errors = 0
    with _connect(db) as c:
        _ensure_schema(c)
        rows = []
        now = datetime.utcnow().isoformat()
        for f in files:
            try:
                h = _sha256_file(f)
                m = json.dumps(_parse_metrics(f))
                rows.append((str(f), h, h, now, m, m))  # both sha256 & content_hash; both metrics cols
            except Exception:
                errors += 1
        with c:
            c.executemany(
                "INSERT OR IGNORE INTO har_entries(path, sha256, content_hash, created_at, metrics_json, metrics) VALUES (?,?,?,?,?,?)",
                rows,
            )
            inserted = c.total_changes
        if checkpoint:
            try:
                c.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            except Exception:
                pass
    dur = time.perf_counter() - start
    return IngestResult(inserted=inserted, skipped=len(files)-inserted, errors=errors, duration_s=dur, checkpointed=checkpoint)
PY
say "wrote: src/gh_copilot/ingest/har.py (exporting ingest_har_entries)"

# -----------------------------------------------------------------------------
# 5) OVERWRITE scripts/database/har_ingestor.py — CLI wrapper calling package fn
# -----------------------------------------------------------------------------
HAR_FILE="$SCRIPTS_DIR/database/har_ingestor.py"
mkdir -p "$(dirname "$HAR_FILE")"
cat > "$HAR_FILE" <<'PY'
#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import typer

# Import the stable entrypoint
try:
    from gh_copilot.ingest.har import ingest_har_entries
except Exception as e:  # source-tree fallback
    import sys
    here = Path(__file__).resolve()
    src = here.parents[2] / "src"
    if src.exists():
        sys.path.insert(0, str(src))
    from gh_copilot.ingest.har import ingest_har_entries  # type: ignore

app = typer.Typer(add_completion=False, help="HAR ingestor (WAL, busy_timeout, batching)")

@app.command()
def main(
    db: Path = typer.Option(Path("analytics.db"), help="Target SQLite DB"),
    checkpoint: bool = typer.Option(False, help="PRAGMA wal_checkpoint(TRUNCATE) after ingest"),
    path: list[Path] = typer.Argument(..., help="HAR files or directories"),
) -> None:
    res = ingest_har_entries(db, path, checkpoint=checkpoint)
    print(json.dumps(res.__dict__, indent=2))

if __name__ == "__main__":
    app()
PY
chmod +x "$HAR_FILE" || true
say "wrote (OVERWROTE): scripts/database/har_ingestor.py"

# -----------------------------------------------------------------------------
# 6) CLI wiring: add generate + migrate-all + ingest-har (stable imports)
# -----------------------------------------------------------------------------
if [[ -f "$CLI_FILE" ]]; then
  if ! grep -q "def migrate_all" "$CLI_FILE"; then
    cat >> "$CLI_FILE" <<'PY'
from __future__ import annotations
import json as _json
from pathlib import Path as _Path
import typer as _typer

try:
    app
except NameError:
    app = _typer.Typer(help="gh_COPILOT CLI")

def _db_path() -> _Path:
    import os as _os
    return _Path(_os.getenv("GH_COPILOT_ANALYTICS_DB", "analytics.db"))

@app.command("migrate-all")
def migrate_all(migrations_dir: _Path = _typer.Option(_Path("databases/migrations"), exists=True)) -> None:
    """Apply *.sql then *.py migrations in lexical order."""
    import importlib.util, sqlite3
    db = _db_path(); conn = sqlite3.connect(db)
    try:
        for sql_file in sorted(migrations_dir.glob("*.sql")):
            sql = sql_file.read_text(encoding="utf-8"); conn.executescript(sql); conn.commit()
            _typer.echo(f"applied: {sql_file.name}")
        for py_file in sorted(migrations_dir.glob("*.py")):
            spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
            mod = importlib.util.module_from_spec(spec); assert spec and spec.loader
            spec.loader.exec_module(mod)  # type: ignore[assignment]
            if hasattr(mod, "upgrade"):
                mod.upgrade(conn); conn.commit(); _typer.echo(f"applied: {py_file.name}")
    finally:
        conn.close()

@app.command("generate")
def generate_cli(
    kind: str = _typer.Argument(..., help="docs|scripts"),
    source_db: _Path = _typer.Option(_Path("documentation.db"), help="DB for templates"),
    out_dir: _Path = _typer.Option(_Path("generated"), help="Output directory"),
    params: str = _typer.Option("", help="JSON substitutions"),
) -> None:
    from gh_copilot.generation.generate_from_templates import generate as _gen
    _ps = _json.loads(params) if params else {}
    written = _gen(kind=kind, source_db=source_db, out_dir=out_dir, analytics_db=_db_path(), params=_ps)
    _typer.echo(_json.dumps({"written": [str(p) for p in written]}, indent=2))

@app.command("ingest-har")
def ingest_har(
    db: _Path = _typer.Option(_Path("analytics.db"), help="Target DB"),
    checkpoint: bool = _typer.Option(False, help="Checkpoint WAL after ingest"),
    path: list[_Path] = _typer.Argument(..., help="HAR files or directories"),
) -> None:
    from gh_copilot.ingest.har import ingest_har_entries
    res = ingest_har_entries(db, path, checkpoint=checkpoint)
    _typer.echo(_json.dumps(res.__dict__, indent=2))
PY
    say "patched CLI: migrate-all, generate, ingest-har"
  else
    info "CLI already contains migrate-all; ensure ingest-har/generate exist"
  fi
else
  warn "CLI file not found at $CLI_FILE — skipping CLI patches"
fi

# -----------------------------------------------------------------------------
# 7) Optional seed for template tables (to avoid generator empty-table failure)
# -----------------------------------------------------------------------------
SEED="$SCRIPTS_DIR/seed_templates.py"
if [[ ! -f "$SEED" ]]; then
  cat > "$SEED" <<'PY'
#!/usr/bin/env python3
from __future__ import annotations
import sqlite3
from pathlib import Path

def seed(db: Path) -> None:
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS documentation_templates(id TEXT PRIMARY KEY, path TEXT NOT NULL, content TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS script_templates(id TEXT PRIMARY KEY, path TEXT NOT NULL, content TEXT NOT NULL);
        INSERT OR IGNORE INTO documentation_templates(id, path, content) VALUES ('readme', 'README', '# Hello {{project}}');
        INSERT OR IGNORE INTO script_templates(id, path, content) VALUES ('hello', 'hello', "print('ok')");
        """
    )
    con.commit(); con.close()

if __name__ == "__main__":
    seed(Path("documentation.db"))
    print("seeded documentation.db with starter templates")
PY
  chmod +x "$SEED" || true
  say "wrote: scripts/seed_templates.py"
fi

# -----------------------------------------------------------------------------
# 8) Final hints
# -----------------------------------------------------------------------------
cat <<'EON'
Next steps (safe path):
  python -m venv .venv && source .venv/bin/activate
  pip install -e ".[dev]"
  gh-copilot migrate-all
  python scripts/seed_templates.py
  python scripts/generate_from_templates.py docs --params '{"project":"gh_COPILOT"}'
  python scripts/database/har_ingestor.py analytics.db path/to/har_dir --checkpoint
  pytest -q
EON
