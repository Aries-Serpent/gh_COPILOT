"""Comprehensive tests for :mod:`artifact_manager` utilities and CLI."""
from __future__ import annotations

import logging
import os
import subprocess
import sys
import difflib
import shutil
from pathlib import Path
from zipfile import ZipFile

import pytest

import artifact_manager
from artifact_manager import LfsPolicy, package_session, recover_latest_session

logger = logging.getLogger(__name__)


def copy_script_to_repo(path: Path) -> None:
    """Copy ``artifact_manager.py`` into ``path`` for CLI execution."""

    global script_dst
    script_dst = path / "artifact_manager.py"
    shutil.copy(Path(__file__).resolve().parents[1] / "artifact_manager.py", script_dst)


def init_repo(path: Path) -> None:
    """Initialize a git repository at ``path``."""

    subprocess.run(["git", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)
    (path / "README.md").write_text("init", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Return a temporary git repository for tests."""

    init_repo(tmp_path)
    return tmp_path


@pytest.fixture
def malformed_policy_repo(tmp_path: Path) -> Path:
    """Repository containing a malformed ``.codex_lfs_policy.yaml``."""

    init_repo(tmp_path)
    policy_file = tmp_path / ".codex_lfs_policy.yaml"
    policy_file.write_text("!bad yaml\n:\n", encoding="utf-8")
    logger.info("Created malformed policy file %s", policy_file)
    yield tmp_path
    logger.info("Cleaning up malformed policy repo %s", tmp_path)


# ---------------------------------------------------------------------------
# Packaging and recovery
# ---------------------------------------------------------------------------


def test_package_and_recover(repo: Path) -> None:
    """Package a session and recover it back into the temp directory."""

    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: true\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    file_path = tmp_dir / "a.txt"
    file_path.write_text("data", encoding="utf-8")
    logger.info("created %s", file_path)

    policy = LfsPolicy(repo)
    archive = package_session(tmp_dir, repo, policy, commit=True, message="test")
    assert archive and archive.exists(), "archive missing"
    log = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], cwd=repo, text=True)
    assert "test" in log, "commit message not found"
    lfs_files = subprocess.check_output(["git", "lfs", "ls-files"], cwd=repo, text=True)
    assert archive.name in lfs_files, "archive not tracked by LFS"

    for p in tmp_dir.iterdir():
        p.unlink()
    assert not any(tmp_dir.iterdir()), "tmp_dir not empty before recovery"
    recovered = recover_latest_session(tmp_dir, repo, policy)
    assert recovered == archive
    assert (tmp_dir / "a.txt").exists()


def test_package_session_no_changes_returns_none(repo: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Packaging with no file changes should return ``None`` and log nothing."""

    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    with caplog.at_level(logging.INFO):
        result = package_session(tmp_dir, repo, LfsPolicy(repo))
    assert result is None, "Expected None when no files changed"
    sessions_dir = repo / "codex_sessions"
    assert not sessions_dir.exists() or not any(sessions_dir.iterdir())
    assert not any(r.levelno >= logging.WARNING for r in caplog.records)


def test_package_session_empty_dir_returns_none(repo: Path, caplog: pytest.LogCaptureFixture) -> None:
    """An empty temporary directory should not produce an archive."""

    empty_dir = repo / "empty_tmp"
    empty_dir.mkdir()
    logger.info("Created empty directory %s", empty_dir)

    try:
        with caplog.at_level(logging.INFO):
            result = package_session(empty_dir, repo, LfsPolicy(repo))
        assert result is None
        sessions_dir = repo / "codex_sessions"
        assert not sessions_dir.exists() or not any(sessions_dir.iterdir())
    finally:
        empty_dir.rmdir()
        logger.info("Removed empty directory %s", empty_dir)


def test_package_session_missing_tmp_dir_returns_none(
    repo: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Return ``None`` when the temporary directory is absent."""

    tmp_dir = repo / "nonexistent"
    logger.info("Invoking package_session with missing tmp_dir %s", tmp_dir)
    with caplog.at_level(logging.INFO):
        result = package_session(tmp_dir, repo, LfsPolicy(repo))
    assert result is None, "Expected None for missing tmp_dir"
    sessions_dir = repo / "codex_sessions"
    assert not sessions_dir.exists() or not any(sessions_dir.iterdir())
    logger.info("No archives created in %s", sessions_dir)


def test_package_session_permission_error(repo: Path, monkeypatch, caplog: pytest.LogCaptureFixture) -> None:
    """Simulate a permission error during packaging and ensure graceful failure."""

    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "f.txt").write_text("data", encoding="utf-8")

    def boom(*args, **kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr(artifact_manager, "create_zip", boom)
    with caplog.at_level(logging.ERROR):
        result = package_session(tmp_dir, repo, LfsPolicy(repo))
    assert result is None
    assert any("denied" in m for m in caplog.messages)


def test_package_session_sessions_dir_mkdir_permission(
    repo: Path, monkeypatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Permission errors creating the session directory are handled."""

    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "s.txt").write_text("data", encoding="utf-8")

    sessions_dir = repo / "codex_sessions"
    orig_mkdir = Path.mkdir

    def fake_mkdir(self, *args, **kwargs):
        if self == sessions_dir:
            raise PermissionError("no access")
        return orig_mkdir(self, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", fake_mkdir)
    with caplog.at_level(logging.ERROR):
        result = package_session(tmp_dir, repo, LfsPolicy(repo))
    assert result is None
    assert any("no access" in m for m in caplog.messages)


def test_package_session_sessions_dir_race(
    repo: Path, monkeypatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Race conditions creating the session directory are logged."""

    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "r.txt").write_text("data", encoding="utf-8")

    sessions_dir = repo / "codex_sessions"
    orig_mkdir = Path.mkdir

    def fake_mkdir(self, *args, **kwargs):
        if self == sessions_dir:
            raise FileExistsError("exists")
        return orig_mkdir(self, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", fake_mkdir)
    with caplog.at_level(logging.ERROR):
        result = package_session(tmp_dir, repo, LfsPolicy(repo))
    assert result is None
    assert any("race condition" in m.lower() for m in caplog.messages)


def test_custom_session_dir(repo: Path) -> None:
    """Respect ``session_artifact_dir`` from policy."""

    policy_content = (
        "enable_autolfs: true\n"
        "session_artifact_dir: custom_sessions\n"
        "gitattributes_template: |\n  *.zip filter=lfs diff=lfs merge=lfs -text\n"
    )
    (repo / ".codex_lfs_policy.yaml").write_text(policy_content, encoding="utf-8")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "b.txt").write_text("data", encoding="utf-8")

    policy = LfsPolicy(repo)
    archive = package_session(tmp_dir, repo, policy)
    assert archive and archive.parent.name == "custom_sessions"


def test_package_session_idempotent(repo: Path) -> None:
    """Running ``package_session`` twice without changes returns ``None`` the second time."""

    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: false\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "c.txt").write_text("data", encoding="utf-8")

    policy = LfsPolicy(repo)
    first = package_session(tmp_dir, repo, policy)
    assert first is not None
    second = package_session(tmp_dir, repo, policy)
    assert second is None


def test_package_without_autolfs(repo: Path) -> None:
    """Packaging should work even when ``enable_autolfs`` is false."""

    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: false\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "d.txt").write_text("data", encoding="utf-8")
    policy = LfsPolicy(repo)
    archive = package_session(tmp_dir, repo, policy)
    assert archive and archive.exists()


def test_cli_sync_gitattributes_updates_file(repo: Path) -> None:
    """CLI ``--sync-gitattributes`` generates file matching the policy."""

    policy = repo / ".codex_lfs_policy.yaml"
    policy.write_text(
        "gitattributes_template: |\n  *.dat filter=lfs diff=lfs merge=lfs -text\n",
        encoding="utf-8",
    )
    copy_script_to_repo(repo)
    result = subprocess.run(
        [sys.executable, str(script_dst), "--sync-gitattributes"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    expected = (
        "# Git LFS rules for binary artifacts\n"
        "*.dat filter=lfs diff=lfs merge=lfs -text\n"
        "codex_sessions/*.zip filter=lfs diff=lfs merge=lfs -text\n"
        "*.db filter=lfs diff=lfs merge=lfs -text\n"
        "*.7z filter=lfs diff=lfs merge=lfs -text\n"
        "*.zip filter=lfs diff=lfs merge=lfs -text\n"
        "*.bak filter=lfs diff=lfs merge=lfs -text\n"
        "*.dot filter=lfs diff=lfs merge=lfs -text\n"
        "*.sqlite filter=lfs diff=lfs merge=lfs -text\n"
        "*.exe filter=lfs diff=lfs merge=lfs -text\n"
        "# End of LFS patterns\n"
    )
    content = (repo / ".gitattributes").read_text(encoding="utf-8")
    if content.strip() != expected.strip():
        diff = "\n".join(
            difflib.unified_diff(expected.splitlines(), content.splitlines())
        )
        pytest.fail(f".gitattributes mismatch:\n{diff}")


def test_cli_sync_gitattributes_failure(tmp_path: Path) -> None:
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


def test_cli_help(repo: Path) -> None:
    """``--help`` should list available CLI options."""

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
    """Packaging should honor a custom ``--tmp-dir`` with nested files."""

    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: true\n")
    custom_tmp = repo / "custom_tmp"
    nested = custom_tmp / "sub/dir"
    nested.mkdir(parents=True)
    (nested / "d.txt").write_text("data", encoding="utf-8")
    (custom_tmp / "sp ace.bin").write_bytes(b"0")
    logger.info("created nested files in %s", custom_tmp)

    copy_script_to_repo(repo)
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
        names = zf.namelist()
        assert "sub/dir/d.txt" in names
        assert "sp ace.bin" in names


def test_cli_tmp_dir_permission_error(repo: Path, monkeypatch) -> None:
    """A non-writable ``--tmp-dir`` should abort packaging."""

    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: true\n")
    bad_tmp = repo / "bad_tmp"
    monkeypatch.chdir(repo)
    monkeypatch.setattr(sys, "argv", ["artifact_manager.py", "--package", "--tmp-dir", str(bad_tmp)])
    monkeypatch.setattr(artifact_manager.os, "access", lambda *args, **kwargs: False)
    with pytest.raises(SystemExit) as exc:
        artifact_manager.main()
    assert exc.value.code != 0


def test_cli_creates_missing_tmp_dir(repo: Path) -> None:
    """Packaging with a non-existent ``--tmp-dir`` should create it."""

    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: true\n")
    missing_tmp = repo / "missing_tmp"
    copy_script_to_repo(repo)
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


def test_policy_file_missing_logs_defaults(repo: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Missing policy file should log default usage."""

    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "e.txt").write_text("data", encoding="utf-8")

    with caplog.at_level(logging.INFO):
        policy = LfsPolicy(repo)
    assert policy.session_artifact_dir == "codex_sessions"
    assert any("default LFS policy values" in m for m in caplog.messages)


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


def test_package_session_atomic_output(repo: Path) -> None:
    """Temporary archive artifacts should be cleaned after packaging."""

    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: false\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "f.txt").write_text("data", encoding="utf-8")

    policy = LfsPolicy(repo)
    archive = package_session(tmp_dir, repo, policy)

    assert archive and archive.exists()
    assert not any(archive.parent.glob("*.tmp"))


def test_package_session_logs_sessions_dir(repo: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Packaging should log the resolved sessions directory."""

    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "log.txt").write_text("data", encoding="utf-8")

    with caplog.at_level(logging.INFO):
        package_session(tmp_dir, repo, LfsPolicy(repo))

    assert any("Session artifacts directory" in m for m in caplog.messages)


def test_invalid_session_dir_value(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Invalid ``session_artifact_dir`` values should fall back to defaults."""

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


def test_malformed_yaml_fallback(
    malformed_policy_repo: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Malformed policy files should emit an error and use defaults."""

    with caplog.at_level(logging.ERROR):
        policy = LfsPolicy(malformed_policy_repo)
    assert policy.session_artifact_dir == "codex_sessions"
    assert not policy.enabled
    assert any("Malformed YAML" in m for m in caplog.messages)


def test_package_session_malformed_policy(
    malformed_policy_repo: Path, caplog: pytest.LogCaptureFixture
) -> None:
    tmp_dir = malformed_policy_repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "l.txt").write_text("data", encoding="utf-8")
    logger.info("Created temporary file in %s", tmp_dir)

    with caplog.at_level(logging.ERROR):
        policy = LfsPolicy(malformed_policy_repo)
        archive = package_session(tmp_dir, malformed_policy_repo, policy)

    assert archive and archive.parent.name == "codex_sessions"
    assert any("Malformed YAML" in m for m in caplog.messages)

    for p in tmp_dir.iterdir():
        p.unlink()
    tmp_dir.rmdir()
    logger.info("Cleaned up temporary directory %s", tmp_dir)


def test_runtime_directory_switch(tmp_path: Path) -> None:
    """Changing the session directory at runtime should place archives accordingly."""

    repo = tmp_path
    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("session_artifact_dir: first\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "h.txt").write_text("data", encoding="utf-8")

    policy = LfsPolicy(repo)
    archive1 = package_session(tmp_dir, repo, policy)
    assert archive1 and archive1.parent.name == "first"

    (repo / ".codex_lfs_policy.yaml").write_text("session_artifact_dir: second\n")
    policy = LfsPolicy(repo)
    (tmp_dir / "i.txt").write_text("data", encoding="utf-8")
    archive2 = package_session(tmp_dir, repo, policy)
    assert archive2 and archive2.parent.name == "second"


def test_cli_help_lists_options(tmp_path: Path) -> None:
    """Ensure CLI help lists key options for discoverability."""

    repo = tmp_path
    init_repo(repo)
    copy_script_to_repo(repo)
    result = subprocess.run(
        [sys.executable, str(script_dst), "--help"],
        cwd=repo,
        text=True,
        capture_output=True,
    )
    for option in [
        "--package",
        "--recover",
        "--commit",
        "--message",
        "--tmp-dir",
        "--sync-gitattributes",
    ]:
        assert option in result.stdout


def test_session_dir_symlink_outside(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Symlinked session dirs escaping the repo should be rejected."""

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
    assert any(
        "escapes repository root" in m or "is a symlink" in m
        for m in caplog.messages
    )
