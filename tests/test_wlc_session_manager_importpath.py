import os
import shutil
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "wlc_session_manager.py"
DEFAULT_DB = Path("databases/production.db")


def test_cli_import_path(tmp_path):
    temp_db = tmp_path / "production.db"
    shutil.copy(DEFAULT_DB, temp_db)
    env = os.environ.copy()
    env["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    env["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backups")
    env["TEST_MODE"] = "1"
    result = subprocess.run(
        [
            "python",
            str(SCRIPT),
            "--steps",
            "1",
            "--db-path",
            str(temp_db),
        ],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
