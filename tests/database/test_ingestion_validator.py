import builtins
import hashlib
import importlib
import sqlite3
import sys


def test_validate_without_numpy(monkeypatch, tmp_path):
    """Validator should fall back when NumPy is unavailable."""
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "numpy":
            raise ImportError
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.delitem(sys.modules, "scripts.database.ingestion_validator", raising=False)
    monkeypatch.delitem(sys.modules, "template_engine.template_synchronizer", raising=False)
    ingestion_validator = importlib.import_module("scripts.database.ingestion_validator")

    workspace = tmp_path / "ws"
    workspace.mkdir()
    file_path = workspace / "doc.txt"
    file_path.write_text("hello", encoding="utf-8")
    digest = hashlib.sha256("hello".encode()).hexdigest()

    db_path = tmp_path / "db.sqlite"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE documentation_assets (doc_path TEXT, content_hash TEXT)"
        )
        conn.execute(
            "CREATE TABLE template_assets (template_path TEXT, content_hash TEXT)"
        )
        conn.execute(
            "INSERT INTO documentation_assets (doc_path, content_hash) VALUES (?, ?)",
            ("doc.txt", digest),
        )

    analytics_db = tmp_path / "analytics.sqlite"
    validator = ingestion_validator.IngestionValidator(workspace, db_path, analytics_db)
    assert validator.validate() is True
    assert ingestion_validator.HAS_NUMPY is False

