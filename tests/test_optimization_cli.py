from pathlib import Path
import os
import shutil

from scripts.optimization.automated_optimization_engine import main as opt_main
from scripts.optimization.intelligence_gathering_system import main as intel_main


def _setup_workspace(tmp_path: Path) -> Path:
    ws = tmp_path
    (ws / "databases").mkdir()
    shutil.copy(Path("databases/production.db"), ws / "databases" / "production.db")
    (ws / "demo.py").write_text("print('hi')\n")
    return ws


def test_automated_optimizer_cli(tmp_path, monkeypatch):
    ws = _setup_workspace(tmp_path)
    events = []

    def fake_log(event, **_):
        events.append(event)
        return True

    monkeypatch.setattr(
        "scripts.optimization.automated_optimization_engine._log_event", fake_log
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    assert opt_main([str(ws)]) == 0
    assert any(e.get("event") == "optimization_metric" for e in events)


def test_intelligence_gather_cli(tmp_path, monkeypatch):
    ws = _setup_workspace(tmp_path)
    events = []

    def fake_log(event, **_):
        events.append(event)
        return True

    monkeypatch.setattr(
        "scripts.optimization.intelligence_gathering_system._log_event", fake_log
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    db = ws / "databases" / "production.db"
    assert intel_main([str(db)]) == 0
    assert any(e.get("event") == "table_summary" for e in events)
