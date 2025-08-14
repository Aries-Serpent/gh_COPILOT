#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
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

app = typer.Typer(help="Generate docs/scripts from DB templates and log events")

@app.command()
def main(
    kind: str = typer.Argument(..., help="docs|scripts"),
    source_db: Path = typer.Option(Path("documentation.db"), help="DB to read templates from"),
    out_dir: Path = typer.Option(Path("generated"), help="Output directory"),
    analytics_db: Path = typer.Option(Path("analytics.db"), help="Analytics DB for event logging"),
    params: str = typer.Option("", help="JSON substitutions, e.g. '{\"project\":\"X\"}'"),
) -> None:
    """
    Generate artifacts from DB templates.

    Args:
        kind: Type of artifact to generate ('docs' or 'scripts').
        source_db: Path to the database containing templates.
        out_dir: Output directory for generated files.
        analytics_db: Path to analytics database for event logging.
        params: JSON string for parameter substitutions.
    """
    try:
        values = json.loads(params) if params else {}
    except json.JSONDecodeError as exc:
        typer.secho(f"Error decoding params JSON: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    try:
        written = _generate(
            kind=kind,
            source_db=source_db,
            out_dir=out_dir,
            analytics_db=analytics_db,
            params=values
        )
        print(json.dumps({"written": [str(p) for p in written]}, indent=2))
    except Exception as exc:
        typer.secho(f"Generation failed: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()