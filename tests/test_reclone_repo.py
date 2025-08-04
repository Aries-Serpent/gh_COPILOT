import os
import subprocess
import sys
from pathlib import Path


def create_source_repo(tmp_path: Path):
    repo = tmp_path / "source"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True)
    (repo / "file.txt").write_text("hello", encoding="utf-8")
    subprocess.run(["git", "add", "file.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True)
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True)
    return repo, result.stdout.strip()


def run_script(args, env=None):
    cmd = [sys.executable, "scripts/reclone_repo.py"] + args
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def test_clone_and_print_commit_hash(tmp_path):
    repo, commit = create_source_repo(tmp_path)
    dest = tmp_path / "clone"
    result = run_script(["--repo-url", str(repo), "--dest", str(dest)])
    assert result.returncode == 0
    assert result.stdout.strip() == commit
    assert (dest / ".git").is_dir()


def test_backup_requires_env(tmp_path):
    repo, _ = create_source_repo(tmp_path)
    dest = tmp_path / "existing"
    dest.mkdir()
    env = os.environ.copy()
    env.pop("GH_COPILOT_BACKUP_ROOT", None)
    result = run_script(["--repo-url", str(repo), "--dest", str(dest), "--backup-existing"], env=env)
    assert result.returncode != 0
    assert "GH_COPILOT_BACKUP_ROOT" in result.stderr
