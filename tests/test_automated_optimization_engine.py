from pathlib import Path

from scripts.optimization.automated_optimization_engine import AutomatedOptimizationEngine


def _setup_workspace(tmp_path: Path) -> Path:
    ws = tmp_path
    (ws / "databases").mkdir()
    (ws / "databases" / "analytics.db").write_text("")
    return ws


def test_optimizer_removes_dead_code(tmp_path, monkeypatch):
    ws = _setup_workspace(tmp_path)
    target = ws / "sample.py"
    target.write_text("def foo():\n    pass\n")
    events = []

    monkeypatch.setattr(
        "scripts.optimization.automated_optimization_engine._log_event",
        lambda e, **_: events.append(e),
    )

    AutomatedOptimizationEngine().optimize(ws)
    assert "pass" not in target.read_text()
    assert any(e.get("event") == "optimization_metric" for e in events)
