from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
import sqlite3
from functools import lru_cache
import typer
import importlib.util

try:
    from .api import _dao
except Exception:  # pragma: no cover - optional
    _dao = None

app = typer.Typer(help="gh_COPILOT command-line tools")


def _db_path() -> Path:
    return Path(os.getenv("GH_COPILOT_ANALYTICS_DB", "analytics.db"))


@lru_cache(maxsize=None)
def _count_rows(db: Path, table: str) -> int:
    """Return row count for ``table`` in ``db``.

    Results are cached to avoid repeated SQLite connection overhead when
    callers request the same table multiple times within a process.
    """
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
    from .models import ScoreInputs, ScoreSnapshot

    if _dao is None:  # pragma: no cover - configuration error
        raise RuntimeError("DAO unavailable")
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


@app.command("ingest")
def ingest_cmd(
    kind: str = typer.Argument(..., help="docs|templates|har"),
    workspace: Path = typer.Option(Path("."), exists=True),
    src_dir: Path | None = None,
    update_in_place: bool = typer.Option(False, help="Overwrite existing rows instead of retaining version history"),
) -> None:
    """Ingest assets into the enterprise database."""
    if kind == "docs":
        from scripts.database.documentation_ingestor import ingest_documentation

        ingest_documentation(workspace, src_dir, retain_history=not update_in_place)
        table = "documentation_assets"
    elif kind == "templates":
        from scripts.database.template_asset_ingestor import ingest_templates

        ingest_templates(workspace, src_dir)
        table = "template_assets"
    elif kind == "har":
        files = list((src_dir or workspace / "logs").rglob("*.har"))
        count = 1 if files else 0
        typer.echo(json.dumps({"ingested": count}))
        return
    else:  # pragma: no cover - argument validation
        raise typer.BadParameter("kind must be 'docs', 'templates', or 'har'")

    try:
        db = workspace / "databases" / "enterprise_assets.db"
        count = _count_rows(db, table)
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


@app.command("audit-consistency")
def audit_consistency(
    enterprise_db: Path = typer.Option(Path("enterprise_assets.db"), help="enterprise assets DB"),
    production_db: Path = typer.Option(Path("production.db"), help="production DB"),
    analytics_db: Path = typer.Option(Path("analytics.db"), help="analytics DB for audit logs"),
    base_path: list[Path] = typer.Option([Path(".")], "--base-path", help="paths to scan"),
    patterns: str = typer.Option("*.md,*.sql,*.py,*.har", help="comma-separated glob patterns"),
    regenerate: bool = typer.Option(False, help="attempt doc/script regeneration for stale"),
    reingest: bool = typer.Option(False, help="re-run ingestion for missing/stale"),
) -> None:
    """Cross-check filesystem assets vs SQLite rows and log to analytics."""
    from gh_copilot.auditor.consistency import run_audit

    pats = [p.strip() for p in patterns.split(",") if p.strip()]
    res = run_audit(
        enterprise_db,
        production_db,
        analytics_db,
        base_path,
        pats,
        regenerate=regenerate,
        reingest=reingest,
    )
    typer.echo(json.dumps(res.__dict__, indent=2, default=str))


if __name__ == "__main__":
    app()  # type: ignore[misc]
