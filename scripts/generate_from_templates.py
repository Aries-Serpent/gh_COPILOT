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
