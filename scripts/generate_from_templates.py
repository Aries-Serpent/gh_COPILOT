# [Script]: generate_docs_scripts
# > Generated: 2025-08-14 06:09:33 | Author: mbaetiong
#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
import typer

# Attempt normal import; fallback to source tree for local development
try:
    import gh_copilot  # type: ignore  # noqa: F401
except Exception:
    here = Path(__file__).resolve()
    src = here.parents[1] / "src"
    if src.exists():
        sys.path.insert(0, str(src))
    import gh_copilot  # type: ignore  # noqa: F401

from gh_copilot.generation.generate_from_templates import generate as _generate

app = typer.Typer(help="Generate docs/scripts from DB templates and log events")


@app.command()
def main(
    kind: str = typer.Argument(..., help="Type to generate: 'docs' or 'scripts'"),
    source_db: Path = typer.Option(
        Path("documentation.db"), help="Database containing template records"
    ),
    out_dir: Path = typer.Option(
        Path("generated"), help="Directory to write generated artifacts"
    ),
    analytics_db: Path = typer.Option(
        Path("analytics.db"), help="Analytics database for event logging"
    ),
    params: str = typer.Option(
        "", help="JSON substitutions e.g. '{\"project\":\"X\"}'"
    ),
) -> None:
    """
    Generate output artifacts (documentation or scripts) based on stored templates.

    - Validates JSON params.
    - Emits JSON list of written file paths.
    - Exits with non-zero on failure.
    """
    try:
        substitutions = json.loads(params) if params else {}
        if not isinstance(substitutions, dict):
            raise ValueError("Params JSON must decode to an object (dict).")
    except Exception as exc:
        typer.secho(f"Error decoding params JSON: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    try:
        written = _generate(
            kind=kind,
            source_db=source_db,
            out_dir=out_dir,
            analytics_db=analytics_db,
            params=substitutions,
        )
        print(json.dumps({"written": [str(p) for p in written]}, indent=2))
    except Exception as exc:
        typer.secho(f"Generation failed: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
