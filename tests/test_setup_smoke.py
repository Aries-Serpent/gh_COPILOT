import os
import subprocess
from pathlib import Path


def test_setup_sh_installs_optional_and_runs_migrations(tmp_path):
    """Smoke test for setup.sh optional flag and migrations."""
    env = os.environ.copy()
    env["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backups")

    log_file = Path("logs/migrations.log")
    before = log_file.stat().st_mtime if log_file.exists() else 0.0

    subprocess.run(["bash", "setup.sh", "--with-test"], check=True, env=env)

    assert log_file.exists() and log_file.stat().st_mtime >= before
