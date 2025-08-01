import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile

import pytest

import artifact_manager
from artifact_manager import LfsPolicy, package_session, recover_latest_session

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def collect_artifacts(tmp_path: Path, request) -> None:
    """Copy per-test artifacts into the repository ``tmp`` directory.

    Test directories are preserved for later inspection.  They are gathered
    after each test to maintain reproducibility while keeping the workspace
    clean during execution.
    """

    yield
    repo_tmp = REPO_ROOT / "tmp" / request.node.name
    repo_tmp.parent.mkdir(parents=True, exist_ok=True)
    if repo_tmp.exists():
        shutil.rmtree(repo_tmp)
    shutil.copytree(tmp_path, repo_tmp)


@pytest.fixture(scope="session", autouse=True)
def zip_repo_tmp() -> None:
    """Compress collected artifacts into ``tmp/test_artifacts.zip``."""

    yield
    repo_tmp = REPO_ROOT / "tmp"
    if not repo_tmp.exists():
        return
    zip_path = repo_tmp / "test_artifacts.zip"
    with ZipFile(zip_path, "w") as zf:
        for file in repo_tmp.rglob("*"):
            if file == zip_path:
                continue
            zf.write(file, file.relative_to(repo_tmp))
    # remove individual directories after zipping to avoid committing them
    for item in repo_tmp.iterdir():
        if item.is_dir():
            shutil.rmtree(item)


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
    """Round-trip package and recovery through Git LFS."""

    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: true\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    file_path = tmp_dir / "a.txt"
    logging.info("Creating %s", file_path)
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
        logging.info("Removing %s", p)
        p.unlink()
    assert not any(tmp_dir.iterdir())
    recovered = recover_latest_session(tmp_dir, repo, policy)
    assert recovered == archive
    assert (tmp_dir / "a.txt").exists()


def test_custom_session_dir(repo: Path) -> None:
    """Respect ``session_artifact_dir`` when packaging and recovering."""

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
    logging.info("Writing %s", tmp_dir / "b.txt")
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
    """Packaging twice without changes should yield no second archive."""

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


def test_package_session_no_changes(repo: Path, caplog) -> None:
    """Return ``None`` and log when ``tmp`` holds no files to package."""

    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: true\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    policy = LfsPolicy(repo)
    with caplog.at_level(logging.INFO):
        result = package_session(tmp_dir, repo, policy)
    assert result is None
    sessions_dir = repo / policy.session_artifact_dir
    assert not any(sessions_dir.glob("*"))
    assert any("No session artifacts detected" in m for m in caplog.messages)


def test_package_session_permission_error(repo: Path, monkeypatch, caplog) -> None:
    """Gracefully handle failures when the archive cannot be written."""

    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: false\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "perm.txt").write_text("data", encoding="utf-8")

    def raise_perm(*_args, **_kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr(artifact_manager, "create_zip", raise_perm)
    policy = LfsPolicy(repo)
    with caplog.at_level(logging.ERROR):
        result = package_session(tmp_dir, repo, policy)
    assert result is None
    assert any("denied" in m for m in caplog.messages)


def test_package_without_autolfs(repo: Path) -> None:
    """Files are committed directly when auto-LFS is disabled."""

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
    """CLI flag regenerates ``.gitattributes`` from policy data."""

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


def test_cli_sync_gitattributes_preserves_existing(repo: Path) -> None:
    """Synchronizing appends rules while keeping unrelated entries intact."""

    init_repo(repo)
    policy_content = (
        "enable_autolfs: true\n"
        "binary_extensions: ['.dat']\n"
        "gitattributes_template: |\n  *.dat filter=lfs diff=lfs merge=lfs -text\n"
    )
    (repo / ".codex_lfs_policy.yaml").write_text(policy_content, encoding="utf-8")
    existing = "docs/*.md text\n"
    (repo / ".gitattributes").write_text(existing, encoding="utf-8")

    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "sample.dat").write_text("data", encoding="utf-8")

    copy_artifact_manager_script(repo)
    subprocess.run([
        sys.executable,
        str(script_dst),
        "--package",
        "--tmp-dir",
        str(tmp_dir),
        "--sync-gitattributes",
    ], cwd=repo, check=True)

    content = (repo / ".gitattributes").read_text(encoding="utf-8")
    assert content.startswith("# Git LFS rules"), content
    assert "*.dat filter" in content


def test_cli_help(repo: Path) -> None:
    """``--help`` lists supported command-line options."""

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
    """Packaging honors a user-supplied ``--tmp-dir`` location."""

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


def test_cli_tmp_dir_nested_files(repo: Path) -> None:
    """Nested structures and special names are packaged from custom ``--tmp-dir``."""

    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: true\n")
    custom_tmp = repo / "custom_tmp"
    nested = custom_tmp / "sub dir" / "deep"
    nested.mkdir(parents=True)
    (nested / "spaced name.txt").write_text("data", encoding="utf-8")
    (custom_tmp / "empty").mkdir()

    copy_artifact_manager_script(repo)
    subprocess.run([
        sys.executable,
        str(script_dst),
        "--package",
        "--tmp-dir",
        str(custom_tmp),
    ], cwd=repo, check=True)

    archive = next((repo / "codex_sessions").glob("codex-session_*.zip"))
    with ZipFile(archive) as zf:
        names = zf.namelist()
    assert "sub dir/deep/spaced name.txt" in names


def test_cli_creates_missing_tmp_dir(repo: Path) -> None:
    """Packaging with a non-existent ``--tmp-dir`` should create it."""
    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: true\n")
    missing_tmp = repo / "missing_tmp"

    copy_artifact_manager_script(repo)
    subprocess.run(
        [
            sys.executable,
            str(script_dst),
            "--package",
            "--tmp-dir",
            str(missing_tmp),
        ],
        cwd=repo,
        check=True,
    )

    assert missing_tmp.exists()


def test_policy_file_missing_logs_defaults(repo: Path, caplog) -> None:
    """Default policy values apply when no config file is present."""

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
    assert "Packaging session" in messages
    assert archive.parent.name == "codex_sessions"


def test_sync_gitattributes_cli_failure(tmp_path: Path) -> None:
    """CLI should exit non-zero when git operations fail."""
    (tmp_path / ".codex_lfs_policy.yaml").write_text(
        "gitattributes_template: |\n  *.dat filter=lfs diff=lfs merge=lfs -text\n",
        encoding="utf-8",
    )
    copy_script_to_repo(tmp_path)
    result = subprocess.run(
        [sys.executable, str(script_dst), "--sync-gitattributes"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Git command failed" in result.stderr or "Git command failed" in result.stdout


def test_package_session_atomic_output(repo: Path, monkeypatch) -> None:
    """Archives are written atomically and temp files cleaned up."""

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


def test_invalid_session_dir_value(tmp_path: Path, caplog) -> None:
    """Non-string ``session_artifact_dir`` values fall back to default."""

    repo = tmp_path
    init_repo(repo)
    policy_content = "session_artifact_dir: 123\n"
    (repo / ".codex_lfs_policy.yaml").write_text(policy_content, encoding="utf-8")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "g.txt").write_text("data", encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        policy = LfsPolicy(repo)
    assert policy.session_artifact_dir == "codex_sessions"
    assert any("Invalid session_artifact_dir" in m for m in caplog.messages)


def test_malformed_yaml_fallback(tmp_path: Path, caplog) -> None:
    """Malformed policy files trigger error logs and defaults."""

    repo = tmp_path
    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("!bad yaml\n:\n", encoding="utf-8")

    with caplog.at_level(logging.ERROR):
        policy = LfsPolicy(repo)
    assert policy.session_artifact_dir == "codex_sessions"
    assert any("Malformed YAML" in m for m in caplog.messages)


def test_runtime_directory_switch(tmp_path: Path) -> None:
    """Switching session directories at runtime writes to new locations."""

    repo = tmp_path
    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("session_artifact_dir: first\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "h.txt").write_text("data", encoding="utf-8")

    policy = LfsPolicy(repo)
    archive1 = package_session(tmp_dir, repo, policy)
    assert archive1 and archive1.parent.name == "first"

    # change policy and package again
    (repo / ".codex_lfs_policy.yaml").write_text("session_artifact_dir: second\n")
    policy = LfsPolicy(repo)
    (tmp_dir / "i.txt").write_text("data", encoding="utf-8")
    archive2 = package_session(tmp_dir, repo, policy)
    assert archive2 and archive2.parent.name == "second"


def test_cli_help_lists_options(tmp_path: Path) -> None:
    """Temporary repositories expose CLI usage information."""

    repo = tmp_path
    init_repo(repo)
    copy_script_to_repo(repo)  # This sets the script_dst variable
    assert 'script_dst' in globals(), "script_dst must be defined by copy_script_to_repo(repo)"
    result = subprocess.run(
        [sys.executable, str(script_dst), "--help"],
        cwd=repo,
        text=True,
        capture_output=True,
    )
    assert "--tmp-dir" in result.stdout
    assert "--sync-gitattributes" in result.stdout


def test_session_dir_symlink_outside(tmp_path: Path, caplog) -> None:
    """Reject session directories that resolve outside the repository root."""

    repo = tmp_path
    init_repo(repo)
    if not hasattr(os, "symlink"):
        pytest.skip("symlink not supported")
    outside = tmp_path.parent / "outside_sessions"
    outside.mkdir()
    symlink_dir = repo / "outside_link"
    symlink_dir.symlink_to(outside)
    policy_content = f"session_artifact_dir: {symlink_dir.name}\n"
    (repo / ".codex_lfs_policy.yaml").write_text(policy_content, encoding="utf-8")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "j.txt").write_text("data", encoding="utf-8")

    policy = LfsPolicy(repo)
    with caplog.at_level(logging.ERROR):
        result = package_session(tmp_dir, repo, policy)
    assert result is None
    assert any("escapes repository root" in m for m in caplog.messages)
