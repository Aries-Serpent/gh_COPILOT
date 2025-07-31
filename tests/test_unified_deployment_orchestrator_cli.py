from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "orchestration"
    / "UNIFIED_DEPLOYMENT_ORCHESTRATOR_CONSOLIDATED.py"
)
DEFAULT_DB = Path("databases/production.db")


def setup_workspace(tmp_path: Path) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    shutil.copy(DEFAULT_DB, db_dir / "production.db")


def run_cli(args: list[str], tmp_path: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    env["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path.parent / "backups")
    env["PYTHONPATH"] = str(Path.cwd())
    return subprocess.run(
        ["python", str(SCRIPT), *args],
        env=env,
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )


def test_start_stop_status(tmp_path: Path) -> None:
    setup_workspace(tmp_path)

    res = run_cli(["--start"], tmp_path)
    assert res.returncode == 0

    res = run_cli(["--status"], tmp_path)
    assert "RUNNING" in res.stdout

    res = run_cli(["--stop"], tmp_path)
    assert res.returncode == 0

    res = run_cli(["--status"], tmp_path)
    assert "STOPPED" in res.stdout
