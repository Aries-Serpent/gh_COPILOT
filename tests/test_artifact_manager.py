import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile

import artifact_manager
import pytest
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


@pytest.fixture(scope="module")
def repo_tmp_root() -> Path:
    root = Path(__file__).resolve().parents[1] / "tmp"
    root.mkdir(exist_ok=True)
    yield root
    archive = root.parent / "tmp_artifacts.zip"
    with ZipFile(archive, "w") as zf:
        for file in root.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(root.parent))


@pytest.fixture
def repo(tmp_path: Path, request, repo_tmp_root: Path) -> Path:
    yield tmp_path
    dst = repo_tmp_root / request.node.name
    shutil.copytree(tmp_path, dst, dirs_exist_ok=True)


def test_package_and_recover(repo: Path) -> None:
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


def test_custom_session_dir(repo: Path) -> None:
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


def test_package_session_idempotent(repo: Path) -> None:
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


def test_package_without_autolfs(repo: Path) -> None:
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


def test_sync_gitattributes_cli(repo: Path) -> None:
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


def test_cli_help(repo: Path) -> None:
    init_repo(repo)
    copy_script_to_repo(repo)
    result = subprocess.run(
        [sys.executable, str(script_dst), "--help"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "--tmp-dir" in result.stdout
    assert "--sync-gitattributes" in result.stdout


def test_cli_tmp_dir_option(repo: Path) -> None:
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


def test_policy_file_missing_logs_defaults(repo: Path, caplog) -> None:
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
    assert archive.parent.name == "codex_sessions"


def test_package_session_atomic_output(repo: Path, monkeypatch) -> None:
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


def test_invalid_session_dir_defaults(repo: Path, caplog) -> None:
    init_repo(repo)
    policy_content = "session_artifact_dir: 123\n"
    (repo / ".codex_lfs_policy.yaml").write_text(policy_content, encoding="utf-8")
    with caplog.at_level(logging.WARNING):
        policy = LfsPolicy(repo)
    assert policy.session_artifact_dir == "codex_sessions"
    assert any("Invalid session_artifact_dir" in m for m in caplog.messages)


def test_unreadable_policy_file(repo: Path, caplog, monkeypatch) -> None:
    init_repo(repo)
    policy_file = repo / ".codex_lfs_policy.yaml"
    policy_file.write_text("enable_autolfs: true\n", encoding="utf-8")

    original_open = Path.open

    def fake_open(self: Path, *args, **kwargs):
        if self == policy_file:
            raise PermissionError("denied")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fake_open)

    with caplog.at_level(logging.ERROR):
        policy = LfsPolicy(repo)
    assert policy.session_artifact_dir == "codex_sessions"
    assert any("Unable to read" in m for m in caplog.messages)


def test_runtime_session_dir_switch(repo: Path) -> None:
    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: false\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "r1.txt").write_text("data", encoding="utf-8")
    policy = LfsPolicy(repo)
    first = package_session(tmp_dir, repo, policy)
    assert first and first.exists()

    # change policy to new directory and package again
    new_policy_content = "session_artifact_dir: switched\n"
    (repo / ".codex_lfs_policy.yaml").write_text(new_policy_content, encoding="utf-8")
    policy2 = LfsPolicy(repo)
    (tmp_dir / "r2.txt").write_text("more", encoding="utf-8")
    second = package_session(tmp_dir, repo, policy2)
    assert second and second.exists()
    assert first.parent.name == "codex_sessions"
    assert second.parent.name == "switched"
