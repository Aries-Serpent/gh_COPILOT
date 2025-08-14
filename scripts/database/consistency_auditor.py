from __future__ import annotations

import json
from pathlib import Path
import typer

from gh_copilot.auditor.consistency import run_audit

app = typer.Typer(add_completion=False)

@app.command()
def main(
    enterprise_db: Path = typer.Option(Path("enterprise_assets.db")),
    production_db: Path = typer.Option(Path("production.db")),
    analytics_db: Path = typer.Option(Path("analytics.db")),
    base_path: list[Path] = typer.Option([Path(".")], "--base-path"),
    patterns: str = typer.Option("*.md,*.sql,*.py,*.har"),
    regenerate: bool = typer.Option(False),
    reingest: bool = typer.Option(False),
) -> None:
    pats = [p.strip() for p in patterns.split(',') if p.strip()]
    res = run_audit(
        enterprise_db,
        production_db,
        analytics_db,
        base_path,
        pats,
        regenerate=regenerate,
        reingest=reingest,
    )
    print(json.dumps(res.__dict__, indent=2, default=str))

if __name__ == "__main__":
    app()
