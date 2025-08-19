"""Helper CLI to parse a HAR file and log analytics events.

This tool is intentionally lightweight and is primarily used by tests to
exercise the logging helpers without touching the main project CLI.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import typer

from utils.analytics_logging import log_event, log_sync_operation

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command("analyze")
def analyze(
    har_path: Path = typer.Argument(..., exists=True, readable=True),
    events_level: str = typer.Option("INFO", help="log level for event rows"),
    status: str = typer.Option("SUCCESS", help="status for sync_events_log"),
):
    """Analyze ``har_path`` and emit analytics events."""

    db_path = os.getenv("ANALYTICS_DB_PATH")

    with har_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    entries = len(data.get("log", {}).get("entries", []))

    log_event(events_level, "har_analyze_started", {"har": str(har_path)}, db_path=db_path)
    log_sync_operation(str(har_path), entries, status, {"entries": entries}, db_path=db_path)
    log_event(events_level, "har_analyze_completed", {"har": str(har_path), "entries": entries}, db_path=db_path)

    typer.echo(f"Analyzed HAR: {har_path} (entries={entries})")


def main() -> None:
    app()


if __name__ == "__main__":  # pragma: no cover
    main()

