"""Shared test fixtures and reporting utilities."""
from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from zipfile import ZipFile

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def collect_artifacts(tmp_path: Path, request) -> None:
    """Log and copy per-test artifacts into ``tmp/<testname>``.

    Each test's temporary directory is stored under the repository ``tmp``
    folder so artifacts can be reviewed after the run without polluting the
    working tree during execution.
    """

    yield

    repo_tmp = REPO_ROOT / "tmp" / request.node.name
    repo_tmp.parent.mkdir(parents=True, exist_ok=True)
    if repo_tmp.exists():
        shutil.rmtree(repo_tmp)
    shutil.copytree(tmp_path, repo_tmp)
    logger.info("collected artifacts for %s into %s", request.node.name, repo_tmp)


@pytest.fixture(scope="session", autouse=True)
def zip_repo_tmp() -> None:
    """Compress the aggregated test artifacts at the end of the session."""

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
    for item in repo_tmp.iterdir():
        if item.is_dir():
            shutil.rmtree(item)


@pytest.fixture(scope="session", autouse=True)
def apply_repo_migrations() -> None:
    """Ensure database migrations are applied before tests run."""

    from scripts.run_migrations import ensure_migrations_applied

    ensure_migrations_applied()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Display a summary of skipped tests and future improvements."""

    skipped = terminalreporter.getreports("skipped")
    if skipped:
        terminalreporter.section("Skipped tests", sep="=")
        for rep in skipped:
            terminalreporter.line(f"{rep.nodeid} - {rep.longrepr}")
    terminalreporter.section("Future work", sep="=")
    terminalreporter.line(
        "Consider extending artifact_manager tests for additional edge cases and CI integration."
    )


def pytest_runtest_setup(item):
    if "hardware" in item.keywords and not os.getenv("QISKIT_IBM_TOKEN"):
        pytest.skip("QISKIT_IBM_TOKEN not set")
