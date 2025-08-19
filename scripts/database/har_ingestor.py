"""
CLI wrapper for HAR ingestion.

Merged features:
- Typer-based modern CLI (preferred).
- Backward-compatible legacy mode using --workspace + optional --har-dir.
- Delegates core logic to ingest_har_entries (unified implementation).
- Graceful fallbacks if package imports fail.
- JSON output summarizing results (inserted, skipped, errors, duration, checkpointed).

Usage (modern):
    ./ingest_har_files.py --db analytics.db path/to/file.har path/to/dir --checkpoint

Legacy (workspace):
    ./ingest_har_files.py --workspace /path/to/workspace --har-dir /path/to/logs

In legacy mode:
- Expects workspace/databases/enterprise_assets.db (created if missing by underlying logic if that logic exists elsewhere).
- Collects *.har under har-dir (default: workspace/logs).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Optional
from types import SimpleNamespace

import typer

from enterprise_modules import compliance
from utils.log_utils import (
    DEFAULT_ANALYTICS_DB,
    log_event as _log_event,
)


def validate_enterprise_operation(*args, **kwargs):
    result = compliance.validate_enterprise_operation(*args, **kwargs)
    _log_event({"event": "validate_enterprise_operation"}, db_path=DEFAULT_ANALYTICS_DB)
    return result


def enforce_anti_recursion(*args, **kwargs):
    result = compliance.enforce_anti_recursion(*args, **kwargs)
    _log_event({"event": "enforce_anti_recursion"}, db_path=DEFAULT_ANALYTICS_DB)
    return result


def log_sync_operation(*args, **kwargs):
    func = getattr(compliance, "log_sync_operation", None)
    if func is None:  # pragma: no cover - fallback for missing attr
        from scripts.database.cross_database_sync_logger import (
            log_sync_operation as func,  # type: ignore
        )
    result = func(*args, **kwargs)
    _log_event({"event": "log_sync_operation"}, db_path=DEFAULT_ANALYTICS_DB)
    return result


def log_event(*args, **kwargs):
    func = getattr(compliance, "log_event", _log_event)
    result = func(*args, **kwargs)
    _log_event({"event": "log_event"}, db_path=DEFAULT_ANALYTICS_DB)
    return result

def check_database_sizes(*args, **kwargs):
    return True

class SecondaryCopilotValidator:
    def validate_corrections(self, files):
        return True


def tqdm(iterable=None, **k):
    return iterable or []


app = typer.Typer(add_completion=False, help="HAR ingestor (WAL, busy_timeout, batching)")

# Attempt to import the canonical ingestion
try:
    from ingest_har_entries import ingest_har_entries, IngestResult  # local sibling
except Exception:
    try:
        from gh_copilot.ingest.har import ingest_har_entries, IngestResult  # type: ignore
    except Exception as exc:  # pragma: no cover
        typer.secho(f"Failed to import ingest_har_entries: {exc}", fg=typer.colors.RED, err=True)
        ingest_har_entries = None  # type: ignore
        IngestResult = None  # type: ignore


def _legacy_discover(workspace: Path, har_dir: Optional[Path]) -> list[Path]:
    logs_dir = har_dir or (workspace / "logs")
    if not logs_dir.exists():
        return []
    return sorted([p for p in logs_dir.rglob("*.har") if p.is_file()])


@app.command("main")
def main(
    db: Path = typer.Option(
        Path("analytics.db"),
        "--db",
        "-d",
        help="Target SQLite DB (modern mode)",
    ),
    checkpoint: bool = typer.Option(
        False, "--checkpoint", help="Run PRAGMA wal_checkpoint(TRUNCATE) after ingest"
    ),
    path: List[Path] = typer.Argument(
        ..., metavar="PATH...", help="HAR files or directories (modern mode)"
    ),
) -> None:
    """Modern mode ingestion (explicit file/dir arguments)."""
    if ingest_har_entries is None:  # type: ignore
        raise typer.Exit(code=1)
    validate_enterprise_operation(str(db))
    enforce_anti_recursion(SimpleNamespace())
    log_sync_operation(db, "har_ingestion_start")
    log_event({"event": "har_ingestion_start"})
    res = ingest_har_entries(db, path, checkpoint=checkpoint)  # type: ignore
    print(json.dumps(res.__dict__, indent=2))


@app.command("legacy")
def legacy(
    workspace: Path = typer.Option(
        ...,
        "--workspace",
        help="Workspace root containing 'databases' directory",
    ),
    har_dir: Optional[Path] = typer.Option(
        None,
        "--har-dir",
        help="Directory containing HAR files (default: workspace/logs)",
    ),
    checkpoint: bool = typer.Option(
        False, "--checkpoint", help="Run WAL checkpoint in legacy DB"
    ),
) -> None:
    """
    Legacy mode mimicking earlier interface: derives DB path from workspace.
    """
    if ingest_har_entries is None:  # type: ignore
        raise typer.Exit(code=1)

    db_dir = workspace / "databases"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "enterprise_assets.db"

    files = _legacy_discover(workspace, har_dir)
    res = ingest_har_entries(db_path, files, checkpoint=checkpoint)  # type: ignore
    print(json.dumps({"workspace": str(workspace), **res.__dict__}, indent=2))


if __name__ == "__main__":
    # Heuristic: if user passed --workspace, route to legacy automatically for convenience
    if any(arg.startswith("--workspace") for arg in sys.argv):
        # Inject command name if omitted
        if len(sys.argv) > 1 and sys.argv[1] not in {"legacy", "main"}:
            sys.argv.insert(1, "legacy")
    elif len(sys.argv) > 1 and sys.argv[1] not in {"legacy", "main"}:
        # Default to modern 'main' if a non-command arg is first
        sys.argv.insert(1, "main")
    app()
