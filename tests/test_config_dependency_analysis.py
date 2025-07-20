import json
from pathlib import Path

import pytest

from scripts.automation.autonomous_database_optimizer_simplified import (
    AutonomousDatabaseOptimizer,
)


@pytest.fixture
def config_workspace(tmp_path: Path):
    workspace = tmp_path
    (workspace / "config").mkdir()
    (workspace / "databases").mkdir()
    (workspace / "logs").mkdir()
    yield workspace


def _write_config(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def test_config_dependency_analysis_basic(config_workspace: Path) -> None:
    _write_config(config_workspace / "config" / "a.json", {"depends_on": "b.json"})
    _write_config(config_workspace / "config" / "b.json", {"depends_on": "a.json"})
    _write_config(
        config_workspace / "config" / "c.json",
        {"depends_on": "missing.json"},
    )
    optimizer = AutonomousDatabaseOptimizer(workspace_path=str(config_workspace))
    report = optimizer.analyze_config_dependencies()

    assert report["dependencies"]["a.json"] == ["b.json"]
    assert report["dependencies"]["b.json"] == ["a.json"]
    assert "missing.json" in report["missing_configs"]
    assert any(
        set(cycle) == {"a.json", "b.json"} for cycle in report["circular_dependencies"]
    )
