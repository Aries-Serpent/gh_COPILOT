from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
import typer

from .api import _dao
from .models import ScoreInputs, ScoreSnapshot

app = typer.Typer(help="gh_COPILOT command-line tools")


def _db_path() -> Path:
    return Path(os.getenv("GH_COPILOT_ANALYTICS_DB", "analytics.db"))


@app.command()
def migrate(migrations_dir: Path = typer.Option(Path("databases/gh_copilot_migrations"), exists=True)) -> None:
    """Apply all SQL migrations in order."""
    import sqlite3

    db = _db_path()
    conn = sqlite3.connect(db)
    try:
        for sql_file in sorted(migrations_dir.glob("*.sql")):
            sql = sql_file.read_text(encoding="utf-8")
            conn.executescript(sql)
            conn.commit()
            typer.echo(f"applied: {sql_file}")
    finally:
        conn.close()


@app.command("seed-models")
def seed_models() -> None:
    """Insert default compliance model rows if missing."""
    import sqlite3
    import datetime

    db = _db_path()
    conn = sqlite3.connect(db)
    conn.execute(
        """
        INSERT OR IGNORE INTO compliance_models(model_id, weights_json, min_score, effective_from)
        VALUES
        ('main-default', '{"lint":0.3,"tests":0.4,"placeholders":0.2,"sessions":0.1}', 0.90, ?),
        ('dev-default',  '{"lint":0.3,"tests":0.4,"placeholders":0.2,"sessions":0.1}', 0.80, ?)
        """,
        (
            datetime.datetime.utcnow().isoformat(),
            datetime.datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()
    typer.echo("seeded default models (main/dev)")


@app.command("compute-score")
def compute_score(
    branch: str = typer.Option("main"),
    lint: float = typer.Option(..., min=0, max=1),
    tests: float = typer.Option(..., min=0, max=1),
    placeholders: float = typer.Option(..., min=0, max=1),
    sessions: float = typer.Option(..., min=0, max=1),
) -> None:
    """Compute and store a score snapshot for a branch."""
    model = _dao.fetch_active_model(branch)
    inputs = ScoreInputs(
        run_id=str(uuid.uuid4()),
        lint=lint,
        tests=tests,
        placeholders=placeholders,
        sessions=sessions,
        model_id=model.model_id,
    )
    score = model.lint * lint + model.tests * tests + model.placeholders * placeholders + model.sessions * sessions
    snap = ScoreSnapshot(branch=branch, score=score, model_id=model.model_id, inputs=inputs)

    _dao.store_score_inputs(inputs)
    _dao.store_score_snapshot(snap)

    result = {"branch": branch, "score": score, "model": model.model_id}
    typer.echo(json.dumps(result, indent=2))


@app.command("serve")
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    import uvicorn

    uvicorn.run("gh_copilot.api:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    app()
