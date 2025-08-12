from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Query

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
