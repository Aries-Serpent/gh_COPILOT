from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Query
from starlette.responses import JSONResponse, StreamingResponse

from .dao import ComplianceDAO

DB_PATH = Path(os.getenv("GH_COPILOT_ANALYTICS_DB", "analytics.db"))
_dao = ComplianceDAO(DB_PATH)
_dao.ensure_views()

app = FastAPI(title="gh_COPILOT — Compliance Summary API", version="0.1.0")


@app.get("/api/v1/compliance/summary")
def get_compliance_summary(branch: str = Query("main"), min_score: float | None = Query(None)) -> JSONResponse:
    summary = _dao.compliance_summary(branch, target_min_score=min_score)
    return JSONResponse(summary.model_dump())


async def _sse_event_stream(branch: str, min_score: float | None) -> AsyncIterator[bytes]:
    last_ts: str | None = None
    while True:
        snap = _dao.latest_snapshot(branch)
        if snap is not None:
            if last_ts is None or snap.ts.isoformat() > last_ts:
                last_ts = snap.ts.isoformat()
                summary = _dao.compliance_summary(branch, target_min_score=min_score)
                payload = json.dumps(summary.model_dump())
                yield f"data: {payload}\n\n".encode("utf-8")
        else:
            if last_ts is None:
                payload = json.dumps(_dao.compliance_summary(branch, target_min_score=min_score).model_dump())
                yield f"data: {payload}\n\n".encode("utf-8")
                last_ts = "sent-initial"
        # keep-alive
        yield b": ping\n\n"
        await asyncio.sleep(10)


@app.get("/api/v1/events")
def sse_events(branch: str = Query("main"), min_score: float | None = Query(None)) -> StreamingResponse:
    gen = _sse_event_stream(branch=branch, min_score=min_score)
    return StreamingResponse(gen, media_type="text/event-stream")


@app.get("/api/v1/health")
def health() -> dict[str, bool]:
    return {"ok": True}


def run(host: str = "127.0.0.1", port: int = 8001) -> None:
    import uvicorn

    uvicorn.run(app, host=host, port=port)

