#!/usr/bin/env bash
set -euo pipefail
# ------------------------------------------------------------
# gh_COPILOT — One‑Shot Repo Refactor
# Purpose:
#   1) Materialize a runnable generator WRAPPER at scripts/generate_from_templates.py
#   2) Ensure package generator exists under src/gh_copilot/generation/
#   3) Add migrations for ingest_events and generation_events (if missing)
#   4) Patch/replace scripts/database/har_ingestor.py with WAL + busy_timeout + batching
#   5) Ensure CLI has `migrate-all` and `generate` subcommands
#   6) Print safe next steps (venv, install, migrate, test)
#
# Idempotent: re-running will skip existing files unless --force is provided.
# ------------------------------------------------------------

FORCE=${1:-}
ROOT_DIR=$(pwd)
SRC_DIR="$ROOT_DIR/src"
PKG_BASE="$SRC_DIR/gh_copilot"
GEN_PKG="$PKG_BASE/generation"
MIG_DIR="$ROOT_DIR/databases/migrations"
SCRIPTS_DIR="$ROOT_DIR/scripts"
DB_DIR="$ROOT_DIR/databases"
CLI_FILE="$PKG_BASE/cli.py"

say() { printf "\033[1;34m[refactor]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[warn]\033[0m %s\n" "$*"; }
info() { printf "\033[0;36m[i]\033[0m %s\n" "$*"; }
err() { printf "\033[1;31m[err]\033[0m %s\n" "$*"; }

need_file() {
  # usage: need_file <path> <<'EOF'
  local path="$1"
  shift
  if [[ -f "$path" && "$FORCE" != "--force" ]]; then
    info "exists: $path (skip). Use --force to overwrite."
    return 0
  fi
  mkdir -p "$(dirname "$path")"
  cat > "$path"
  say "wrote: $path"
  return 0
}

append_if_missing() {
  # usage: append_if_missing <file> <pattern> <<'EOF'
  local file="$1"; local pattern="$2"
  shift 2
  if [[ -f "$file" ]] && grep -qE "$pattern" "$file"; then
    info "patch present in: $file (skip)"
    return 0
  fi
  mkdir -p "$(dirname "$file")"
  [[ -f "$file" ]] || touch "$file"
  cat >> "$file"
  say "appended patch to: $file"
}

ensure_dep_in_pyproject() {
  local dep="$1"
  local py="$ROOT_DIR/pyproject.toml"
  if [[ -f "$py" ]]; then
    if grep -qi "$dep" "$py"; then
      info "pyproject already contains $dep"
      return 0
    fi
    warn "pyproject.toml exists; add $dep under [project].dependencies if needed."
    return 0
  fi
  say "creating minimal pyproject.toml"
  cat > "$py" <<'PYTOML'
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "gh-copilot"
version = "0.0.4"
description = "gh_COPILOT — generator + HAR WAL bootstrap"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.110",
  "uvicorn[standard]>=0.23",
  "pydantic>=2.6",
  "typer[all]>=0.12"
]

[project.optional-dependencies]
dev = ["pytest>=8.2", "ruff>=0.5", "mypy>=1.10"]

[project.scripts]
gh-copilot = "gh_copilot.cli:app"
PYTOML
}

mkdir -p "$GEN_PKG" "$MIG_DIR" "$SCRIPTS_DIR" "$DB_DIR" "$PKG_BASE"
ensure_dep_in_pyproject "typer"

# ------------------------------------------------------------------
# 1) WRAPPER at scripts/generate_from_templates.py (required by Set 3)
# ------------------------------------------------------------------
need_file "$SCRIPTS_DIR/generate_from_templates.py" WRAP <<'PY'
#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
import typer

# Ensure package import works whether installed or from source tree
try:
    import gh_copilot  # type: ignore
except Exception:
    here = Path(__file__).resolve()
    src = here.parents[1] / "src"
    if src.exists():
        sys.path.insert(0, str(src))
    import gh_copilot  # type: ignore

from gh_copilot.generation.generate_from_templates import generate as _generate

app = typer.Typer(help="DB-first template generation wrapper (docs|scripts)")

@app.command()
def main(
    kind: str = typer.Argument(..., help="docs|scripts"),
    source_db: Path = typer.Option(Path("documentation.db"), help="DB to read templates from"),
    out_dir: Path = typer.Option(Path("generated"), help="Output directory"),
    analytics_db: Path = typer.Option(Path("analytics.db"), help="Analytics DB for event logging"),
    params: str = typer.Option("", help="JSON substitutions, e.g. '{\"project\":\"X\"}'"),
) -> None:
    values = json.loads(params) if params else {}
    written = _generate(kind=kind, source_db=source_db, out_dir=out_dir, analytics_db=analytics_db, params=values)
    print(json.dumps({"written": [str(p) for p in written]}, indent=2))

if __name__ == "__main__":
    app()
PY
chmod +x "$SCRIPTS_DIR/generate_from_templates.py" || true

# ------------------------------------------------------------------
# 2) PACKAGE generator (only if missing)
# ------------------------------------------------------------------
need_file "$GEN_PKG/__init__.py" GENINIT <<'PY'
__all__ = ["dao", "generate_from_templates"]
PY

need_file "$GEN_PKG/dao.py" GENDOA <<'PY'
from __future__ import annotations
import sqlite3, json
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

PRAGMAS = ("PRAGMA journal_mode=WAL;", "PRAGMA synchronous=NORMAL;", "PRAGMA foreign_keys=ON;", "PRAGMA busy_timeout=10000;")

def get_conn(db: Path) -> sqlite3.Connection:
    c = sqlite3.connect(db); c.row_factory = sqlite3.Row
    for p in PRAGMAS: c.execute(p)
    return c

class GenerationDAO:
    def __init__(self, analytics_db: Path): self.analytics_db = analytics_db
    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        c = get_conn(self.analytics_db)
        try: yield c
        finally: c.close()

    def log_event(self, kind: str, source: str, target_path: str, template_id: str|None, inputs: dict) -> None:
        with self._conn() as c, c:
            c.execute(
                "INSERT INTO generation_events(kind, source, target_path, template_id, inputs_json, ts) VALUES (?,?,?,?,?,?)",
                (kind, source, target_path, template_id, json.dumps(inputs), datetime.utcnow().isoformat()),
            )
PY

need_file "$GEN_PKG/generate_from_templates.py" GENMAIN <<'PY'
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
    conn = sqlite3.connect(db); conn.row_factory = sqlite3.Row
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

# ------------------------------------------------------------------
# 3) Migrations for event logging (idempotent)
# ------------------------------------------------------------------
need_file "$MIG_DIR/0004_ingest_events.sql" MIG4 <<'SQL'
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS ingest_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,
  path TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  metrics_json TEXT,
  ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ingest_events_ts ON ingest_events(ts DESC);
SQL

need_file "$MIG_DIR/0005_generation_events.sql" MIG5 <<'SQL'
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS generation_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,
  source TEXT NOT NULL,
  target_path TEXT NOT NULL,
  template_id TEXT,
  inputs_json TEXT,
  ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_generation_events_ts ON generation_events(ts DESC);
SQL

# Optional: HAR table (if your repo hasn't added it yet)
need_file "$MIG_DIR/0006_har_entries.sql" MIG6 <<'SQL'
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS har_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  path TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  created_at TEXT NOT NULL,
  metrics_json TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_har_entries_path_sha ON har_entries(path, sha256);
SQL

# ------------------------------------------------------------------
# 4) CLI ensure: migrate-all + generate subcommands (alias-safe)
# ------------------------------------------------------------------
append_if_missing "$PKG_BASE/__init__.py" "__all__" CLIINIT <<'PY'
__all__ = ["generation"]
PY

append_if_missing "$CLI_FILE" "def generate_cli\(" CLIGEN <<'PY'
from __future__ import annotations
import json as _json
from pathlib import Path as _Path
import typer as _typer

try:
    app
except NameError:  # create minimal Typer app if missing
    app = _typer.Typer(help="gh_COPILOT CLI")

def _db_path() -> _Path:
    import os as _os
    return _Path(_os.getenv("GH_COPILOT_ANALYTICS_DB", "analytics.db"))

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
PY

# ------------------------------------------------------------------
# 5) HAR ingestor retrofit (WAL + busy_timeout + batched tx + optional checkpoint)
# ------------------------------------------------------------------
HAR_FILE="$ROOT_DIR/scripts/database/har_ingestor.py"
mkdir -p "$(dirname "$HAR_FILE")"

if [[ -f "$HAR_FILE" && "$FORCE" != "--force" ]]; then
  warn "har_ingestor.py exists — writing wal-enabled version to har_ingestor.py.new (use --force to overwrite)"
  OUTFILE="$HAR_FILE.new"
else
  OUTFILE="$HAR_FILE"
fi

cat > "$OUTFILE" <<'PY'
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
PY

if [[ "$OUTFILE" != "$HAR_FILE" ]]; then
  say "review generated HAR ingestor at: $OUTFILE then mv to $HAR_FILE if acceptable"
else
  say "wrote: $HAR_FILE"
fi

# ------------------------------------------------------------------
# 6) Hints / Next steps
# ------------------------------------------------------------------
cat <<'EON'

Next steps (safe order):
  1) python -m venv .venv && source .venv/bin/activate
  2) pip install -e ".[dev]"
  3) python -c "import gh_copilot, sys; print('package OK')" || echo 'install warning'
  4) gh-copilot migrate-all    # applies migrations (0004..0006)
  5) python scripts/generate_from_templates.py docs --params '{"project":"gh_COPILOT"}'
  6) python scripts/database/har_ingestor.py analytics.db path/to/har_dir --checkpoint
  7) pytest -q

FAQ
— How to materialize and run safely?
  • This script is the materialization. Save it as: repo_oneshot_refactor.sh
  • Run: bash repo_oneshot_refactor.sh  (or: bash repo_oneshot_refactor.sh --force to overwrite files)

— How to retrofit har_ingestor.py?
  • This script writes a WAL-enabled ingestor at scripts/database/har_ingestor.py (or .new if a file exists).
  • It uses PRAGMA journal_mode=WAL, busy_timeout=10000, synchronous=NORMAL, and a single batched transaction.
  • Optional checkpoint via --checkpoint or env GH_COPILOT_WAL_CHECKPOINT=1.

EON

