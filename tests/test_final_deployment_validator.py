import sqlite3
from pathlib import Path
from deployment.deployment_package_20250710_182951.scripts.final_deployment_validator import EnterpriseUtility


def test_final_deployment_validator(tmp_path):
    workspace = tmp_path
    db_dir = workspace / "databases"
    db_dir.mkdir()
    db_path = db_dir / "production.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE enterprise_readiness_final (production_ready INTEGER)"
        )
        conn.execute(
            "INSERT INTO enterprise_readiness_final VALUES (1)"
        )
    (workspace / "deployment_config.json").write_text("{}")

    util = EnterpriseUtility(workspace_path=str(workspace))
    assert util.execute_utility() is True
