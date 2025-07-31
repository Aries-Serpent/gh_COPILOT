import os
import subprocess
from pathlib import Path

SCRIPT = Path("tools/git_safe_add_commit.py").resolve()


def init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)
    (path / "README.md").write_text("init", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)


def test_autolfs_enabled(tmp_path: Path) -> None:
    init_repo(tmp_path)
    bin_file = tmp_path / "data.bin"
    bin_file.write_bytes(b"\x00\x01\x02")
    subprocess.run(["git", "add", str(bin_file)], cwd=tmp_path, check=True)

    env = os.environ.copy()
    env["ALLOW_AUTOLFS"] = "1"
    env["PYTHONPATH"] = str(Path.cwd())
    proc = subprocess.run([
        "python",
        str(SCRIPT),
        "test",
    ], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "[LFS] Tracking *.bin" in proc.stdout

    gitattributes = (tmp_path / ".gitattributes").read_text(encoding="utf-8")
    assert "*.bin" in gitattributes


def test_autolfs_disabled(tmp_path: Path) -> None:
    init_repo(tmp_path)
    bin_file = tmp_path / "data.bin"
    bin_file.write_bytes(b"\x00\x01\x02")
    subprocess.run(["git", "add", str(bin_file)], cwd=tmp_path, check=True)

    env = os.environ.copy()
    env.pop("ALLOW_AUTOLFS", None)
    env["PYTHONPATH"] = str(Path.cwd())
    proc = subprocess.run([
        "python",
        str(SCRIPT),
        "test",
    ], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert proc.returncode == 1
    assert "Binary or large file detected" in proc.stdout
    assert not (tmp_path / ".gitattributes").exists()
