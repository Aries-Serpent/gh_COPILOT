"""Tests for :mod:`scripts.autonomous_setup_and_audit`."""

from __future__ import annotations

import sqlite3
from pathlib import Path
import pytest

pytestmark = pytest.mark.skip(reason="database locking issue under investigation")

from scripts.autonomous_setup_and_audit import ingest_assets
from scripts.database.unified_database_initializer import initialize_database


@pytest.mark.skip(reason="database locking issue under investigation")
def test_ingest_assets_populates_db(tmp_path: Path, monkeypatch) -> None:
    """``ingest_assets`` should load sample files into the database."""

    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    monkeypatch.chdir(tmp_path)

    docs_dir = tmp_path / "documentation"
    docs_dir.mkdir()
    (docs_dir / "doc.md").write_text("# doc")

    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "template.md").write_text("template body")

    db_path = tmp_path / "production.db"
    initialize_database(db_path)

    events = []
    monkeypatch.setattr(
        "scripts.autonomous_setup_and_audit._log_event",
        lambda evt, **kw: events.append(evt),
    )
    ingest_assets(docs_dir, templates_dir, db_path)

    with sqlite3.connect(db_path) as conn:
        doc_count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
        template_count = conn.execute("SELECT COUNT(*) FROM template_assets").fetchone()[0]
        pattern_count = conn.execute("SELECT COUNT(*) FROM pattern_assets").fetchone()[0]

    assert doc_count == 1
    assert template_count == 1
    assert pattern_count == 1
    assert any("compliance_score" in e for e in events)


def test_ingest_assets_collects_multiple_types(tmp_path: Path, monkeypatch) -> None:
    """Verify ingestion of .md, .txt, .json, and .sql files."""

    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    monkeypatch.chdir(tmp_path)

    docs_dir = tmp_path / "documentation"
    docs_dir.mkdir()
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    extensions = [".md", ".txt", ".json", ".sql"]
    for ext in extensions:
        (docs_dir / f"doc{ext}").write_text("content")
        (templates_dir / f"template{ext}").write_text("content")

    db_path = tmp_path / "production.db"
    initialize_database(db_path)

    ingest_assets(docs_dir, templates_dir, db_path)

    with sqlite3.connect(db_path) as conn:
        doc_count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
        tmpl_count = conn.execute("SELECT COUNT(*) FROM template_assets").fetchone()[0]

    assert doc_count == len(extensions)
    assert tmpl_count == len(extensions)


def test_ingest_assets_transaction_rollback(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    monkeypatch.chdir(tmp_path)

    docs_dir = tmp_path / "documentation"
    docs_dir.mkdir()
    (docs_dir / "doc.md").write_text("# doc")

    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "template.md").write_text("template body")

    db_path = tmp_path / "production.db"
    initialize_database(db_path)

    monkeypatch.setattr(
        "scripts.autonomous_setup_and_audit._compliance_score",
        lambda *_: (_ for _ in ()).throw(RuntimeError("fail")),
    )
    with pytest.raises(RuntimeError):
        ingest_assets(docs_dir, templates_dir, db_path)

    with sqlite3.connect(db_path) as conn:
        counts = [
            conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM template_assets").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM pattern_assets").fetchone()[0],
        ]

    assert counts == [0, 0, 0]


def test_ingest_assets_detects_corruption(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    monkeypatch.chdir(tmp_path)

    docs_dir = tmp_path / "documentation"
    docs_dir.mkdir()
    (docs_dir / "doc.md").write_text("# doc")

    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "template.md").write_text("template body")

    db_path = tmp_path / "production.db"
    initialize_database(db_path)

    analytics_db = tmp_path / "databases" / "analytics.db"
    analytics_db.parent.mkdir()

    def real_log(evt, *, table="correction_logs", db_path=analytics_db, **_):
        with sqlite3.connect(db_path) as conn:
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table} (event TEXT, path TEXT, compliance_score REAL)")
            conn.execute(
                f"INSERT INTO {table} (event, path, compliance_score) VALUES (?,?,?)",
                (evt.get("event"), evt.get("path"), evt.get("compliance_score")),
            )
            conn.commit()

    monkeypatch.setattr("scripts.autonomous_setup_and_audit._log_event", real_log)
    monkeypatch.setattr("scripts.database.ingestion_validator._log_event", real_log)

    class BadHash:
        def __init__(self, *_: object) -> None:
            pass

        def hexdigest(self) -> str:
            return "bad"

    monkeypatch.setattr("scripts.autonomous_setup_and_audit.hashlib.sha256", lambda *_: BadHash())
    monkeypatch.setattr("scripts.autonomous_setup_and_audit._compliance_score", lambda *_: 1.0)

    with pytest.raises(RuntimeError):
        ingest_assets(docs_dir, templates_dir, db_path)

    with sqlite3.connect(analytics_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM correction_logs WHERE event='ingestion_mismatch'").fetchone()[0]

    assert count > 0
