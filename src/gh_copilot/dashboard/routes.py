from __future__ import annotations
try:
    from gh_copilot.dashboard.app import router  # type: ignore
except Exception:
    from fastapi import APIRouter
    router = APIRouter()
    @router.get("/dashboard/corrections/logs")
    def correction_logs():
        return {"items": [], "total": 0}
