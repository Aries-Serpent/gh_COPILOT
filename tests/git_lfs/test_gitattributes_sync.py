import shutil
import subprocess
from pathlib import Path

from artifact_manager import LfsPolicy


def init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)
    (path / "README.md").write_text("init", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)


def run_sync(path: Path) -> None:
    policy = LfsPolicy(path)
    policy.sync_gitattributes()


def test_gitattributes_created(tmp_path: Path) -> None:
    init_repo(tmp_path)
    policy = tmp_path / ".codex_lfs_policy.yaml"
    policy.write_text(
        "gitattributes_template: |\n  *.dat filter=lfs diff=lfs merge=lfs -text\n",
        encoding="utf-8",
    )
    run_sync(tmp_path)
    assert (tmp_path / ".gitattributes").exists()
    content = (tmp_path / ".gitattributes").read_text(encoding="utf-8")
    assert "*.dat" in content


def test_sync_updates_with_new_extension(tmp_path: Path) -> None:
    init_repo(tmp_path)
    policy = tmp_path / ".codex_lfs_policy.yaml"
    policy.write_text(
        "gitattributes_template: |\n  *.dat filter=lfs diff=lfs merge=lfs -text\n",
        encoding="utf-8",
    )
    run_sync(tmp_path)
    policy.write_text(
        "gitattributes_template: |\n  *.dat filter=lfs diff=lfs merge=lfs -text\n"
        "binary_extensions:\n  - .dat\n  - .bin\n",
        encoding="utf-8",
    )
    run_sync(tmp_path)
    content = (tmp_path / ".gitattributes").read_text(encoding="utf-8")
    assert "*.bin" in content


def test_sync_uses_session_dir(tmp_path: Path) -> None:
    init_repo(tmp_path)
    policy = tmp_path / ".codex_lfs_policy.yaml"
    policy.write_text(
        "session_artifact_dir: custom_sessions\n"
        "gitattributes_template: |\n  *.zip filter=lfs diff=lfs merge=lfs -text\n",
        encoding="utf-8",
    )
    run_sync(tmp_path)
    content = (tmp_path / ".gitattributes").read_text(encoding="utf-8")
    assert "custom_sessions/*.zip" in content
