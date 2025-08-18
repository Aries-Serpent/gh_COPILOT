from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from scripts.ml.deploy_models import deploy_model


def _make_registry(tmp_path: Path) -> Path:
    registry = tmp_path / "registry"
    model_dir = registry / "MyModel" / "1"
    model_dir.mkdir(parents=True)
    (model_dir / "model.txt").write_text("data")
    return registry


def test_deploy_model_success(tmp_path, monkeypatch):
    registry = _make_registry(tmp_path)
    workspace = tmp_path / "workspace"
    analytics_db = tmp_path / "analytics.db"

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("MODEL_REGISTRY_URI", str(registry))
    monkeypatch.setenv("MODEL_NAME", "MyModel")
    monkeypatch.setenv("MODEL_VERSION", "1")

    deploy_model(analytics_db=analytics_db)

    artifact_dir = workspace / "artifacts" / "models" / "MyModel" / "1"
    assert (artifact_dir / "model.txt").exists()
    with sqlite3.connect(analytics_db) as conn:
        row = conn.execute(
            "SELECT status, artifact_hashes FROM model_deployments"
        ).fetchone()
        assert row[0] == "success"
        hashes = json.loads(row[1])
        expected = hashlib.sha256((artifact_dir / "model.txt").read_bytes()).hexdigest()
        assert hashes["model.txt"] == expected


def test_deploy_model_failure_triggers_rollback(tmp_path, monkeypatch):
    registry = _make_registry(tmp_path)
    workspace = tmp_path / "workspace"
    analytics_db = tmp_path / "analytics.db"

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("MODEL_REGISTRY_URI", str(registry))
    monkeypatch.setenv("MODEL_NAME", "MyModel")
    monkeypatch.setenv("MODEL_VERSION", "1")

    def bad_health_check(path: Path) -> bool:  # pragma: no cover - trivial
        return False

    deploy_model(analytics_db=analytics_db, health_check=bad_health_check)

    artifact_dir = workspace / "artifacts" / "models" / "MyModel" / "1"
    assert not artifact_dir.exists()
    with sqlite3.connect(analytics_db) as conn:
        row = conn.execute("SELECT status FROM model_deployments").fetchone()
        assert row[0] == "failure"

