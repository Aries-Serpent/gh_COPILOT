import json
import os
import sqlite3
from pathlib import Path

from scripts.database.har_asset_ingestor import ingest_har_entries
from scripts.database.unified_database_initializer import initialize_database


def _write_har(path: Path, comment: str) -> None:
    data = {"log": {"comment": comment, "entries": []}}
    path.write_text(json.dumps(data))


def test_har_ingestor_stores_content_and_skips_duplicates(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path
    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)
    db_dir = workspace / "databases"
    db_dir.mkdir()
    db_path = db_dir / "enterprise_assets.db"
    initialize_database(db_path)

    logs_dir = workspace / "logs"
    logs_dir.mkdir()
    file1 = logs_dir / "a.har"
    file2 = logs_dir / "b.har"
    _write_har(file1, "first")
    _write_har(file2, "first")  # duplicate content

    ingest_har_entries(workspace, logs_dir)

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT har_path, content_hash, md5, raw_content, content_size FROM har_entries"
        ).fetchall()

    assert len(rows) == 1
    path, sha256, md5, raw, size = rows[0]
    assert path.endswith("a.har") or path.endswith("b.har")
    assert json.loads(raw)["log"]["comment"] == "first"
    assert size == len(raw.encode())
    # simple duplicate check: hash of file1 equals stored hash
    content = file1.read_bytes()
    assert sha256 == __import__("hashlib").sha256(content).hexdigest()
    assert md5 == __import__("hashlib").md5(content).hexdigest()

