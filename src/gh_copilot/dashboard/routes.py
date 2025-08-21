from __future__ import annotations
from typing import Any

try:
    from gh_copilot.dashboard.app import router  # type: ignore
except Exception:
    import pytest

    fastapi = pytest.importorskip("fastapi", reason="FastAPI not installed")

    router = fastapi.APIRouter()

    @router.get("/dashboard/corrections/logs")
    def correction_logs() -> dict[str, int | list[Any]]:
        return {"items": [], "total": 0}
