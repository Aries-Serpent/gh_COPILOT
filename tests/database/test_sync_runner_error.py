import logging
from pathlib import Path
from typing import Dict, List, Tuple

import pytest

from src.database.engine import Engine
from src.database.sync_runner import run_sync


def test_run_sync_logs_errors(tmp_path: Path, monkeypatch, caplog) -> None:
    db1 = tmp_path / "a.db"
    db2 = tmp_path / "b.db"
    Engine(db1).execute("CREATE TABLE t (id INTEGER)")
    Engine(db2).execute("CREATE TABLE t (id INTEGER)")

    def failing_sync(self: Engine, other: Engine) -> None:  # pragma: no cover - test replacement
        raise RuntimeError("boom")

    monkeypatch.setattr(Engine, "sync_with", failing_sync)

    events: List[Tuple[str, Dict[str, str]]] = []

    def hook(event: str, ctx: Dict[str, str]) -> None:
        events.append((event, ctx))

    with pytest.raises(RuntimeError):
        with caplog.at_level(logging.ERROR):
            run_sync(db1, db2, log_hook=hook)

    assert any(name == "sync.error" for name, _ in events)
    assert any("Sync failed" in record.getMessage() for record in caplog.records)

