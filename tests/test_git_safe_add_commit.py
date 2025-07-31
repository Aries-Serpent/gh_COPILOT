import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path("tools/git_safe_add_commit.py").resolve()


def init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)
    (path / "README.md").write_text("init", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
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
