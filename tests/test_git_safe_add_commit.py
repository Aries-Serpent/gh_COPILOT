import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path("tools/git_safe_add_commit.py").resolve()
SH_SCRIPT = Path("tools/git_safe_add_commit.sh").resolve()


def init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)
    (path / "README.md").write_text("init", encoding="utf-8")
    docs = path / "docs"
    docs.mkdir()
    (docs / "GOVERNANCE_STANDARDS.md").write_text("rules", encoding="utf-8")
    subprocess.run(
        ["git", "add", "README.md", "docs/GOVERNANCE_STANDARDS.md"],
        cwd=path,
        check=True,
    )
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)


def test_binary_file_tracked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    init_repo(tmp_path)
    bin_file = tmp_path / "data.bin"
    bin_file.write_bytes(b"\x00\x01\x02")
    subprocess.run(["git", "add", str(bin_file)], cwd=tmp_path, check=True)

    env = os.environ.copy()
    env["ALLOW_AUTOLFS"] = "1"
    env["PYTHONPATH"] = str(Path.cwd())
    subprocess.run(["python", str(SCRIPT), "test"], cwd=tmp_path, env=env, check=True)

    gitattributes = (tmp_path / ".gitattributes").read_text(encoding="utf-8")
    assert "*.bin" in gitattributes


def test_large_file_tracked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    init_repo(tmp_path)
    big = tmp_path / "big.dat"
    big.write_bytes(b"0" * (2 * 1024 * 1024))
    subprocess.run(["git", "add", str(big)], cwd=tmp_path, check=True)

    policy = tmp_path / ".codex_lfs_policy.yaml"
    policy.write_text("size_threshold_mb: 1\n", encoding="utf-8")

    env = os.environ.copy()
    env["ALLOW_AUTOLFS"] = "1"
    env["PYTHONPATH"] = str(Path.cwd())
    subprocess.run(["python", str(SCRIPT), "big"], cwd=tmp_path, env=env, check=True)

    gitattributes = (tmp_path / ".gitattributes").read_text(encoding="utf-8")
    assert "*.dat" in gitattributes


def test_commit_blocked_without_allow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    init_repo(tmp_path)
    f = tmp_path / "fail.bin"
    f.write_bytes(b"\x00\x01")
    subprocess.run(["git", "add", str(f)], cwd=tmp_path, check=True)

    env = os.environ.copy()
    env.pop("ALLOW_AUTOLFS", None)
    env["PYTHONPATH"] = str(Path.cwd())
    result = subprocess.run(["python", str(SCRIPT), "fail"], cwd=tmp_path, env=env)
    assert result.returncode != 0


def test_help(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())
    proc = subprocess.run(["python", str(SCRIPT), "-h"], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert proc.returncode == 0
    assert "ALLOW_AUTOLFS" in proc.stdout


def test_missing_governance_doc(tmp_path: Path) -> None:
    init_repo(tmp_path)
    (tmp_path / "docs" / "GOVERNANCE_STANDARDS.md").unlink()
    new_file = tmp_path / "data.txt"
    new_file.write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", str(new_file)], cwd=tmp_path, check=True)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())
    result = subprocess.run(["python", str(SCRIPT), "msg"], cwd=tmp_path, env=env)
    assert result.returncode != 0


def test_shell_help(tmp_path: Path) -> None:
    proc = subprocess.run(["bash", str(SH_SCRIPT), "-h"], cwd=tmp_path, capture_output=True, text=True)
    assert proc.returncode == 0
    assert "ALLOW_AUTOLFS" in proc.stdout


def test_session_logs_auto_added(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    init_repo(tmp_path)
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    session_db = db_dir / "codex_session_logs.db"
    session_db.write_bytes(b"0")

    env = os.environ.copy()
    env["ALLOW_AUTOLFS"] = "1"
    env["PYTHONPATH"] = str(Path.cwd())
    subprocess.run(["python", str(SCRIPT), "msg"], cwd=tmp_path, env=env, check=True)

    tracked = subprocess.run(
        ["git", "ls-files"], cwd=tmp_path, text=True, capture_output=True, check=True
    ).stdout.splitlines()
    assert "databases/codex_session_logs.db" in tracked
    gitattributes = (tmp_path / ".gitattributes").read_text(encoding="utf-8")
    assert "*.db" in gitattributes
