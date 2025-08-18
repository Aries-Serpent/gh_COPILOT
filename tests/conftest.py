"""Shared test fixtures and reporting utilities."""
# pyright: reportAttributeAccessIssue=false, reportInvalidTypeForm=false, reportReturnType=false
from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from zipfile import ZipFile

import pytest
import sqlite3
import sys
import types


def _ensure_stub(mod_name: str, submods: list[str] | None = None) -> None:
    if mod_name in sys.modules:
        return
    try:
        __import__(mod_name)
        return
    except Exception:
        stub = types.ModuleType(mod_name)
        sys.modules[mod_name] = stub
        for sub in (submods or []):
            full = f'{mod_name}.{sub}'
            sys.modules[full] = types.ModuleType(full)

_ensure_stub('qiskit', ['algorithms','quantum_info','transpiler','providers'])
try:
    import scripts.wlc_session_manager as wsm
except Exception:  # pragma: no cover - fallback when optional deps missing
    class _WsmStub:
        @staticmethod
        def ensure_session_table(conn):
            conn.execute(
                "CREATE TABLE IF NOT EXISTS unified_wrapup_sessions (id INTEGER)"
            )
    wsm = _WsmStub()

# Provide a stub monitoring module for tests to avoid optional dependency errors.
monitoring_stub = types.ModuleType("monitoring")


class BaselineAnomalyDetector:  # minimal placeholder
    def __init__(self, db_path=None):
        self.threshold = 0.0

    def zscores(self):
        return []

    def detect(self):
        return []


monitoring_stub.BaselineAnomalyDetector = BaselineAnomalyDetector
sys.modules["monitoring"] = monitoring_stub
health_monitor_stub = types.ModuleType("monitoring.health_monitor")
health_monitor_stub.gather_metrics = lambda *a, **k: []
sys.modules["monitoring.health_monitor"] = health_monitor_stub

# Enable test mode to prevent side effects such as database writes.
os.environ.setdefault("TEST_MODE", "1")


@pytest.fixture(autouse=True)
def enforce_test_mode(monkeypatch):
    """Ensure TEST_MODE is set for each test run."""
    monkeypatch.setenv("TEST_MODE", "1")

REPO_ROOT = Path(__file__).resolve().parents[1]
logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def set_workspace_env(monkeypatch):
    """Provide a default workspace path for modules expecting it."""
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(REPO_ROOT))


@pytest.fixture(scope="session")
def unified_wrapup_session_db(tmp_path_factory):
    """Provide a temporary database with the unified_wrapup_sessions table."""
    db_dir = tmp_path_factory.mktemp("wrapup_db")
    db_file = db_dir / "production.db"
    with sqlite3.connect(db_file) as conn:
        wsm.ensure_session_table(conn)
    return db_file


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
    import sqlite3

    try:
        ensure_migrations_applied()
    except sqlite3.DatabaseError:
        # Skip migration if the database file is not initialized
        pass


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
