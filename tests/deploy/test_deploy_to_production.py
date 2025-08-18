import os
import sqlite3
import subprocess
import sys

from deployment.scripts import deploy_to_production as deploy_mod


def test_deploy_dry_run(tmp_path):
    db = tmp_path / "analytics.db"
    env = {**os.environ, "GH_COPILOT_ANALYTICS_DB": str(db)}
    result = subprocess.run(
        [sys.executable, "-m", "deployment.scripts.deploy_to_production", "--dry-run"],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    assert "Dry run deployment plan" in result.stdout
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT event, status FROM deployment_events").fetchall()
    conn.close()
    assert ("dry_run", "planned") in rows


def test_deploy_failure_triggers_rollback(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    monkeypatch.setenv("GH_COPILOT_ANALYTICS_DB", str(db))
    monkeypatch.setattr(deploy_mod, "ANALYTICS_DB", db)
    called = {}

    def fail(_):
        raise RuntimeError("boom")

    def fake_rollback():
        called["rolled_back"] = True

    monkeypatch.setattr(deploy_mod, "migrate_environment", fail)
    monkeypatch.setattr(deploy_mod, "rollback", fake_rollback)

    result = deploy_mod.deploy(
        deploy_mod.DeploymentRequest(environment="production"), dry_run=False
    )
    assert not result.success
    assert called.get("rolled_back")
    conn = sqlite3.connect(db)
    events = [row[0] for row in conn.execute("SELECT event FROM deployment_events")]
    conn.close()
    assert "failure" in events and "rolled_back" in events
