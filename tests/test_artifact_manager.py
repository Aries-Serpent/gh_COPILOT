import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile

import artifact_manager
from artifact_manager import LfsPolicy, package_session, recover_latest_session


def copy_script_to_repo(path: Path) -> None:
    """Copy ``artifact_manager.py`` into the temporary git repo for CLI tests."""
    global script_dst
    script_dst = path / "artifact_manager.py"
    shutil.copy(Path(__file__).resolve().parents[1] / "artifact_manager.py", script_dst)


def copy_artifact_manager_script(path: Path) -> None:
    """Alias used by some tests."""
    copy_script_to_repo(path)


def init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)
    (path / "README.md").write_text("init", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)


def test_package_and_recover(tmp_path: Path) -> None:
    repo = tmp_path
    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: true\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    file_path = tmp_dir / "a.txt"
    file_path.write_text("data", encoding="utf-8")

    policy = LfsPolicy(repo)
    archive = package_session(tmp_dir, repo, policy, commit=True, message="test")
    assert archive and archive.exists()
    log = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], cwd=repo, text=True)
    assert "test" in log
    lfs_files = subprocess.check_output(["git", "lfs", "ls-files"], cwd=repo, text=True)
    assert archive.name in lfs_files

    # remove file and recover
    for p in tmp_dir.iterdir():
        p.unlink()
    assert not any(tmp_dir.iterdir())
    recovered = recover_latest_session(tmp_dir, repo, policy)
    assert recovered == archive
    assert (tmp_dir / "a.txt").exists()


def test_custom_session_dir(tmp_path: Path) -> None:
    repo = tmp_path
    init_repo(repo)
    policy_content = (
        "enable_autolfs: true\n"
        "session_artifact_dir: custom_sessions\n"
        "gitattributes_template: |\n"
        "  *.db filter=lfs diff=lfs merge=lfs -text\n"
    )
    (repo / ".codex_lfs_policy.yaml").write_text(policy_content, encoding="utf-8")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "b.txt").write_text("data", encoding="utf-8")

    policy = LfsPolicy(repo)
    assert policy.session_artifact_dir == "custom_sessions"
    policy.sync_gitattributes()
    attrs = (repo / ".gitattributes").read_text(encoding="utf-8")
    assert "custom_sessions/*.zip" in attrs

    archive = package_session(tmp_dir, repo, policy, commit=True)
    assert archive.parent.name == "custom_sessions"

    lfs_files = subprocess.check_output(["git", "lfs", "ls-files"], cwd=repo, text=True)
    assert archive.name in lfs_files

    assert not (tmp_dir / "b.txt").exists()
    recovered = recover_latest_session(tmp_dir, repo, policy)
    assert recovered == archive
    assert (tmp_dir / "b.txt").exists()


def test_package_session_idempotent(tmp_path: Path) -> None:
    repo = tmp_path
    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: true\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "c.txt").write_text("data", encoding="utf-8")

    policy = LfsPolicy(repo)
    first = package_session(tmp_dir, repo, policy)
    assert first and first.exists()

    # second run should detect no changes after cleanup
    result = package_session(tmp_dir, repo, policy)
    assert result is None


def test_package_without_autolfs(tmp_path: Path) -> None:
    repo = tmp_path
    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: false\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "c.txt").write_text("data", encoding="utf-8")

    policy = LfsPolicy(repo)
    archive = package_session(tmp_dir, repo, policy, commit=True, message="test")
    assert archive and archive.exists()
    lfs_files = subprocess.check_output(["git", "lfs", "ls-files"], cwd=repo, text=True)
    assert archive.name not in lfs_files


def test_sync_gitattributes_cli(tmp_path: Path) -> None:
    repo = tmp_path
    init_repo(repo)
    policy_content = (
        "enable_autolfs: true\n"
        "binary_extensions: ['.dat', '.bin']\n"
        "gitattributes_template: |\n  *.dat filter=lfs diff=lfs merge=lfs -text\n"
    )
    (repo / ".codex_lfs_policy.yaml").write_text(policy_content, encoding="utf-8")
    gitattributes = repo / ".gitattributes"
    gitattributes.write_text("old", encoding="utf-8")

    copy_script_to_repo(repo)
    subprocess.run(
        [sys.executable, str(script_dst), "--sync-gitattributes"],
        cwd=repo,
        check=True,
    )

    content = gitattributes.read_text(encoding="utf-8")
    assert "Git LFS rules for binary artifacts" in content
    assert "*.dat" in content
    assert "*.bin" in content


def test_cli_tmp_dir_option(tmp_path: Path) -> None:
    repo = tmp_path
    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: true\n")
    custom_tmp = repo / "custom_tmp"
    custom_tmp.mkdir()
    (custom_tmp / "d.txt").write_text("data", encoding="utf-8")

    copy_artifact_manager_script(repo)
    subprocess.run(
        [
            sys.executable,
            str(script_dst),
            "--package",
            "--tmp-dir",
            str(custom_tmp),
        ],
        cwd=repo,
        check=True,
    )

    sessions_dir = repo / "codex_sessions"
    archives = sorted(sessions_dir.glob("codex-session_*.zip"))
    assert archives
    with ZipFile(archives[0]) as zf:
        assert "d.txt" in zf.namelist()


def test_policy_file_missing_logs_defaults(tmp_path: Path, caplog) -> None:
    repo = tmp_path
    init_repo(repo)
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "e.txt").write_text("data", encoding="utf-8")

    with caplog.at_level(logging.INFO):
        policy = LfsPolicy(repo)
        archive = package_session(tmp_dir, repo, policy)

    assert archive and archive.exists()
    messages = " ".join(caplog.messages)
    assert "not found" in messages
    assert "Using default LFS policy values" in messages
    assert "Session artifact directory" in messages
    assert archive.parent.name == "codex_sessions"


def test_package_session_atomic_output(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path
    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: false\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "f.txt").write_text("data", encoding="utf-8")

    recorded: dict[str, Path] = {}

    def fake_create_zip(archive_path: Path, files: Iterable[Path], base_dir: Path) -> None:
        recorded["tmp"] = archive_path
        with ZipFile(archive_path, "w") as zf:
            for file in files:
                zf.write(file, arcname=file.relative_to(base_dir))

    monkeypatch.setattr(artifact_manager, "create_zip", fake_create_zip)

    policy = LfsPolicy(repo)
    archive = package_session(tmp_dir, repo, policy)

    assert archive and archive.exists()
    temp_path = recorded["tmp"]
    assert temp_path.parent == archive.parent
    assert temp_path.suffix == ".tmp"
    assert not temp_path.exists()
