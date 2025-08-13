from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
import sqlite3
import typer
import importlib.util

from .api import _dao
from .models import ScoreInputs, ScoreSnapshot

app = typer.Typer(help="gh_COPILOT command-line tools")


def _db_path() -> Path:
    return Path(os.getenv("GH_COPILOT_ANALYTICS_DB", "analytics.db"))


def _count_rows(db: Path, table: str) -> int:
    """Return row count for ``table`` in ``db``."""
    with sqlite3.connect(db) as conn:
        try:
            cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
            return int(cur.fetchone()[0])
        except sqlite3.Error:
            return 0


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


@app.command("migrate-all")
def migrate_all(migrations_dir: Path = typer.Option(Path("databases/migrations"), exists=True)) -> None:
    """Apply *.sql then *.py migrations in lexical order."""
    db = _db_path()
    conn = sqlite3.connect(db)
    try:
        for sql_file in sorted(migrations_dir.glob("*.sql")):
            sql = sql_file.read_text(encoding="utf-8")
            conn.executescript(sql)
            conn.commit()
            typer.echo(f"applied: {sql_file.name}")
        for py_file in sorted(migrations_dir.glob("*.py")):
            spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
            mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
            assert spec and spec.loader
            spec.loader.exec_module(mod)  # type: ignore[assignment]
            if hasattr(mod, "upgrade"):
                mod.upgrade(conn)  # type: ignore[arg-type]
                conn.commit()
                typer.echo(f"applied: {py_file.name}")
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


@app.command("ingest-docs")
def ingest_docs(
    workspace: Path = typer.Option(Path("."), exists=True),
    docs_dir: Path | None = None,
    update_in_place: bool = typer.Option(
        False,
        help="Overwrite existing rows instead of retaining version history",
    ),
) -> None:
    """Ingest documentation into the enterprise assets database."""
    from scripts.database.documentation_ingestor import ingest_documentation

    try:
        ingest_documentation(workspace, docs_dir, retain_history=not update_in_place)
        db = workspace / "databases" / "enterprise_assets.db"
        count = _count_rows(db, "documentation_assets")
        typer.echo(json.dumps({"ingested": count}))
    except Exception as exc:  # pragma: no cover - surfaced via exit code
        typer.echo(str(exc), err=True)
        raise typer.Exit(1)


@app.command("ingest-templates")
def ingest_templates_cmd(
    workspace: Path = typer.Option(Path("."), exists=True),
    templates_dir: Path | None = None,
) -> None:
    """Ingest templates into the enterprise assets database."""
    from scripts.database.template_asset_ingestor import ingest_templates

    try:
        ingest_templates(workspace, templates_dir)
        db = workspace / "databases" / "enterprise_assets.db"
        count = _count_rows(db, "template_assets")
        typer.echo(json.dumps({"ingested": count}))
    except Exception as exc:  # pragma: no cover - surfaced via exit code
        typer.echo(str(exc), err=True)
        raise typer.Exit(1)


@app.command("ingest-har")
def ingest_har_cmd(
    workspace: Path = typer.Option(Path("."), exists=True),
    har_dir: Path | None = None,
) -> None:
    """Ingest HAR files into the enterprise assets database."""
    from scripts.database.har_ingestor import ingest_har_entries

    try:
        ingest_har_entries(workspace, har_dir)
        db = workspace / "databases" / "enterprise_assets.db"
        count = _count_rows(db, "har_entries")
        typer.echo(json.dumps({"ingested": count}))
    except Exception as exc:  # pragma: no cover - surfaced via exit code
        typer.echo(str(exc), err=True)
        raise typer.Exit(1)


@app.command("generate-docs")
def generate_docs(
    db_path: Path = typer.Option(Path("databases/production.db")),
    analytics_db: Path = typer.Option(Path("databases/analytics.db")),
) -> None:
    """Generate documentation metrics and output them as JSON."""
    from scripts import generate_docs_metrics

    try:
        generate_docs_metrics.main(["--db-path", str(db_path), "--analytics-db", str(analytics_db)])
        metrics = generate_docs_metrics.get_metrics(db_path)
        typer.echo(json.dumps(metrics))
    except Exception as exc:  # pragma: no cover - surfaced via exit code
        typer.echo(str(exc), err=True)
        raise typer.Exit(1)


@app.command("generate")
def generate_cli(
    kind: str = typer.Argument(..., help="docs|scripts"),
    source_db: Path = typer.Option(Path("documentation.db"), help="DB for templates"),
    out_dir: Path = typer.Option(Path("generated"), help="Output directory"),
    params: str = typer.Option("", help="JSON substitutions"),
) -> None:
    """Generate docs or scripts from templates and log the event."""
    from gh_copilot.generation.generate_from_templates import generate as gen

    values = json.loads(params) if params else {}
    written = gen(kind=kind, source_db=source_db, out_dir=out_dir, analytics_db=_db_path(), params=values)
    typer.echo(json.dumps({"written": [str(p) for p in written]}, indent=2))


if __name__ == "__main__":
    app()
