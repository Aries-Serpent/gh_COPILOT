import hashlib
import logging
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from enterprise_modules.compliance import pid_recursion_guard as compliance_pid_guard
from scripts.database.documentation_ingestor import (
    ingest_documentation,
    pid_recursion_guard,
)
from scripts.database.unified_database_initializer import initialize_database


def test_ingest_documentation(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path
    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)
    db_dir = workspace / "databases"
    db_dir.mkdir()
    db_path = db_dir / "enterprise_assets.db"
    docs_dir = workspace / "documentation"
    docs_dir.mkdir()
    doc = docs_dir / "guide.md"
    doc.write_text("# Guide")
    ingest_documentation(workspace, docs_dir)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT doc_path, modified_at FROM documentation_assets").fetchone()
        ops = conn.execute("SELECT COUNT(*) FROM cross_database_sync_operations").fetchone()[0]
    assert row[0].endswith("guide.md")
    assert row[1] is not None
    assert ops >= 1


def test_zero_byte_file_skipped(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path
    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)
    db_dir = workspace / "databases"
    db_dir.mkdir()
    db_path = db_dir / "enterprise_assets.db"
    initialize_database(db_path)
    docs_dir = workspace / "documentation"
    docs_dir.mkdir()
    (docs_dir / "empty.md").write_text("")
    ingest_documentation(workspace, docs_dir)
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
        ops = conn.execute("SELECT COUNT(*) FROM cross_database_sync_operations").fetchone()[0]
    assert count == 0
    assert ops >= 1


def test_duplicate_document_skipped(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    db_dir = workspace / "databases"
    db_dir.mkdir()
    docs_dir = workspace / "documentation"
    docs_dir.mkdir()
    (docs_dir / "a.md").write_text("# Guide")
    (docs_dir / "b.md").write_text("# Guide")
    ingest_documentation(workspace, docs_dir)
    db_path = db_dir / "enterprise_assets.db"
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
    assert count == 1


def test_missing_directory(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path
    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)
    db_dir = workspace / "databases"
    db_dir.mkdir()
    docs_dir = workspace / "missing"
    ingest_documentation(workspace, docs_dir)
    db_path = db_dir / "enterprise_assets.db"
    with sqlite3.connect(db_path) as conn:
        ops = conn.execute("SELECT COUNT(*) FROM cross_database_sync_operations").fetchone()[0]
        count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
    assert ops >= 1
    assert count == 0


def test_duplicate_content_skipped(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path
    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)
    db_dir = workspace / "databases"
    db_dir.mkdir()
    docs_dir = workspace / "documentation"
    docs_dir.mkdir()
    (docs_dir / "a.md").write_text("# Guide")
    (docs_dir / "b.md").write_text("# Guide")
    ingest_documentation(workspace, docs_dir)
    db_path = db_dir / "enterprise_assets.db"
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
    assert count == 1


def test_reingest_logs_duplicate(tmp_path: Path, caplog, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    db_dir = workspace / "databases"
    db_dir.mkdir()
    docs_dir = workspace / "documentation"
    docs_dir.mkdir()
    doc = docs_dir / "guide.md"
    content = "# Guide\n"
    doc.write_text(content)
    ingest_documentation(workspace, docs_dir)
    caplog.clear()
    caplog.set_level(logging.INFO)
    ingest_documentation(workspace, docs_dir)
    messages = " ".join(caplog.messages)
    assert "UNCHANGED" in messages
    db_path = db_dir / "enterprise_assets.db"
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
    assert count == 1


def test_cli_in_place_flag(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path
    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)
    db_dir = workspace / "databases"
    db_dir.mkdir()
    docs_dir = workspace / "documentation"
    docs_dir.mkdir()
    doc = docs_dir / "guide.md"
    doc.write_text("first")
    module = "scripts.database.documentation_ingestor"
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        [sys.executable, "-m", module, "--workspace", str(workspace), "--docs-dir", str(docs_dir), "--in-place"],
        check=True,
        cwd=repo_root,
    )
    doc.write_text("second")
    subprocess.run(
        [sys.executable, "-m", module, "--workspace", str(workspace), "--docs-dir", str(docs_dir), "--in-place"],
        check=True,
        cwd=repo_root,
    )
    with sqlite3.connect(db_dir / "enterprise_assets.db") as conn:
        row = conn.execute(
            "SELECT version, content_hash FROM documentation_assets WHERE doc_path=?",
            (str(doc.relative_to(workspace)),),
        ).fetchone()
    assert row[0] == 2
    assert row[1] == hashlib.sha256("second".encode()).hexdigest()


def test_pid_recursion_guard_exposed() -> None:
    """Ensure the pid_recursion_guard decorator is imported correctly."""
    assert pid_recursion_guard is compliance_pid_guard
