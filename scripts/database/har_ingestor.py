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

__all__ = ["ingest_har_entries", "app"]

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
