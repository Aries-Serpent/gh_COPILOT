from __future__ import annotations

import os
from pathlib import Path
from fastapi import BackgroundTasks, FastAPI, Query

from .dao import SQLiteAnalyticsDAO

app = FastAPI(title="gh_COPILOT API", version="0.0.1")

_DB = Path(os.getenv("GH_COPILOT_ANALYTICS_DB", "analytics.db"))
_dao = SQLiteAnalyticsDAO(_DB)


@app.get("/api/v1/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.get("/api/v1/placeholders")
def get_placeholders(status: str = Query("open")):
    return [p.model_dump() for p in _dao.fetch_placeholders(status=status)]


@app.get("/api/v1/compliance")
def get_compliance(branch: str = Query("main")):
    snap = _dao.fetch_score(branch)
    return snap.model_dump() if snap else {"branch": branch, "score": None}


@app.post("/api/v1/ingest")
def api_ingest(kind: str = Query(..., regex="^(docs|templates|har)$")) -> dict[str, bool]:
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", "."))
    if kind == "docs":
        from scripts.database.documentation_ingestor import ingest_documentation

        ingest_documentation(workspace)
    elif kind == "templates":
        from scripts.database.template_asset_ingestor import ingest_templates

        ingest_templates(workspace)
    else:
        from scripts.database.har_ingestor import ingest_har_entries

        ingest_har_entries(workspace)
    return {"ok": True}


@app.post("/api/v1/regenerate/{kind}")
def api_regenerate(kind: str, params: dict | None = None) -> dict[str, list[str]]:
    from gh_copilot.generation.generate_from_templates import generate as gen

    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", "."))
    source = workspace / ("documentation.db" if kind == "docs" else "production.db")
    out_dir = workspace / "generated"
    written = gen(kind=kind, source_db=source, out_dir=out_dir, analytics_db=_DB, params=params or {})
    return {"written": [str(p) for p in written]}


@app.post("/api/v1/audit-consistency")
def api_audit_consistency(
    background_tasks: BackgroundTasks,
    enterprise_db: str = Query("enterprise_assets.db"),
    production_db: str = Query("production.db"),
    analytics_db: str = Query("analytics.db"),
    base_path: str = Query("."),
    patterns: str = Query("*.md,*.sql,*.py,*.har"),
    regenerate: bool = Query(False),
    reingest: bool = Query(False),
) -> dict[str, str]:
    from gh_copilot.auditor.consistency import run_audit
    from pathlib import Path

    pats = [p.strip() for p in patterns.split(",") if p.strip()]
    background_tasks.add_task(
        run_audit,
        Path(enterprise_db),
        Path(production_db),
        Path(analytics_db),
        [Path(base_path)],
        pats,
        regenerate=regenerate,
        reingest=reingest,
    )
    return {"status": "scheduled"}
