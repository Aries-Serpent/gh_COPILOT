from __future__ import annotations

import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "git_safe_add_commit.py"


def run(cmd, cwd, env=None):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, env=env, check=True)


def test_git_safe_add_commit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    run(["git", "init"], cwd=repo)
    run(["git", "config", "user.email", "test@example.com"], cwd=repo)
    run(["git", "config", "user.name", "Tester"], cwd=repo)

    (repo / "file.txt").write_text("hello")
    (repo / "bin.bin").write_bytes(b"\x00\x01\x02")
    run(["git", "add", "file.txt", "bin.bin"], cwd=repo)

    env = os.environ.copy()
    env["ALLOW_AUTOLFS"] = "1"
    run(["python", str(SCRIPT), "test commit"], cwd=repo, env=env)

    attrs = (repo / ".gitattributes").read_text()
    assert "*.bin" in attrs
    log = run(["git", "log", "-1", "--pretty=%B"], cwd=repo)
    assert "test commit" in log.stdout
