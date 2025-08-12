import sqlite3
from pathlib import Path

import pytest

# The compliance module may be optional in minimal environments. Skip the test
# suite gracefully when it is unavailable.
pytest.importorskip("enterprise_modules.compliance")
from enterprise_modules.compliance import pid_recursion_guard as compliance_pid_guard

from scripts.database.documentation_ingestor import (
    ingest_documentation,
    pid_recursion_guard,
    _PID_GUARD_AVAILABLE,
)


def test_duplicate_detection(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    db_dir = workspace / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    monkeypatch.setenv("ANALYTICS_DB", str(analytics_db))
    docs_dir = workspace / "documentation"
    docs_dir.mkdir()
    (docs_dir / "a.md").write_text("# Guide")
    (docs_dir / "b.md").write_text("# Guide")
    ingest_documentation(workspace, docs_dir)
    with sqlite3.connect(db_dir / "enterprise_assets.db") as conn:
        count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
    assert count == 1
    with sqlite3.connect(analytics_db) as conn:
        module_events = conn.execute(
            "SELECT COUNT(*) FROM event_log WHERE module=?",
            ("documentation_ingestor",),
        ).fetchone()[0]
    assert module_events == 2


def test_validator_invoked(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    db_dir = workspace / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    monkeypatch.setenv("ANALYTICS_DB", str(analytics_db))
    docs_dir = workspace / "documentation"
    docs_dir.mkdir()
    doc = docs_dir / "guide.md"
    doc.write_text("# Guide")

    called: dict[str, list[str]] = {}

    class DummyValidator:
        def validate_corrections(self, files: list[str]) -> bool:  # pragma: no cover - simple stub
            called["files"] = files
            return True

    monkeypatch.setattr(
        "scripts.database.documentation_ingestor.SecondaryCopilotValidator",
        lambda: DummyValidator(),
    )

    ingest_documentation(workspace, docs_dir)
    assert called["files"] == [str(doc)]


@pytest.mark.skipif(not _PID_GUARD_AVAILABLE, reason="pid_recursion_guard not available")
def test_pid_recursion_guard_exposed() -> None:
    """Ensure the pid_recursion_guard decorator is imported correctly."""
    assert pid_recursion_guard is compliance_pid_guard
