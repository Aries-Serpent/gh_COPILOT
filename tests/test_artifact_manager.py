import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile

from artifact_manager import LfsPolicy, package_session, recover_latest_session


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
    policy_content = "enable_autolfs: true\nsession_artifact_dir: custom_sessions\n"
    (repo / ".codex_lfs_policy.yaml").write_text(policy_content, encoding="utf-8")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "b.txt").write_text("data", encoding="utf-8")

    policy = LfsPolicy(repo)
    archive = package_session(tmp_dir, repo, policy)
    assert archive.parent.name == "custom_sessions"

    (tmp_dir / "b.txt").unlink()
    recovered = recover_latest_session(tmp_dir, repo, policy)
    assert recovered == archive
    assert (tmp_dir / "b.txt").exists()


def test_package_no_changes_returns_none(tmp_path: Path) -> None:
    repo = tmp_path
    init_repo(repo)
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    policy = LfsPolicy(repo)
    archive = package_session(tmp_dir, repo, policy)
    assert archive is None
    assert not (repo / policy.session_artifact_dir).exists()


def test_package_without_autolfs(tmp_path: Path) -> None:
    repo = tmp_path
    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: false\n")
    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (tmp_dir / "c.txt").write_text("data", encoding="utf-8")

    policy = LfsPolicy(repo)
    archive = package_session(tmp_dir, repo, policy, commit=True, message="no lfs")
    assert archive and archive.exists()
    lfs_files = subprocess.check_output(["git", "lfs", "ls-files"], cwd=repo, text=True)
    assert archive.name not in lfs_files


def test_tmp_dir_option_honored(tmp_path: Path) -> None:
    repo = tmp_path
    init_repo(repo)
    (repo / ".codex_lfs_policy.yaml").write_text("enable_autolfs: true\n")
    custom_tmp = repo / "session_tmp"
    custom_tmp.mkdir()
    (custom_tmp / "d.txt").write_text("data", encoding="utf-8")

    script = Path(__file__).resolve().parents[1] / "artifact_manager.py"
    shutil.copy(script, repo / "artifact_manager.py")
    subprocess.run(
        ["python", "artifact_manager.py", "--package", "--tmp-dir", "session_tmp"],
        cwd=repo,
        check=True,
    )

    archives = list((repo / "codex_sessions").glob("codex-session_*.zip"))
    assert archives
    with ZipFile(archives[0]) as zf:
        assert "d.txt" in zf.namelist()
