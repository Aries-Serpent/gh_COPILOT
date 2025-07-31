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
