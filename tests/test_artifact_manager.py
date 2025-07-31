import shutil
import subprocess
from pathlib import Path

from artifact_manager import LfsPolicy, package_session, recover_latest_session


def init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=path, check=True)
    (path / "README.md").write_text("init", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)


def copy_policy(repo: Path) -> None:
    policy_src = Path(__file__).resolve().parents[1] / ".codex_lfs_policy.yaml"
    shutil.copy(policy_src, repo / ".codex_lfs_policy.yaml")


def test_package_and_recover(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    copy_policy(repo)

    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    sample = tmp_dir / "sample.txt"
    sample.write_text("data", encoding="utf-8")
    subprocess.run(["git", "add", str(sample)], cwd=repo, check=True)

    policy = LfsPolicy(repo)
    archive = package_session(tmp_dir, repo, policy)
    assert archive is not None and archive.exists()

    subprocess.run(["git", "add", str(archive), ".gitattributes"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "archive"], cwd=repo, check=True, stdout=subprocess.DEVNULL)

    gitattributes = (repo / ".gitattributes").read_text(encoding="utf-8")
    assert "filter=lfs" in gitattributes

    result = subprocess.run(["git", "lfs", "ls-files"], cwd=repo, check=True, capture_output=True, text=True)
    assert archive.name in result.stdout

    shutil.rmtree(tmp_dir)
    tmp_dir.mkdir()

    restored = recover_latest_session(tmp_dir, repo)
    assert restored == archive
    assert (tmp_dir / "sample.txt").exists()


def test_package_no_changes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    copy_policy(repo)

    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()

    policy = LfsPolicy(repo)
    archive = package_session(tmp_dir, repo, policy)
    assert archive is None
