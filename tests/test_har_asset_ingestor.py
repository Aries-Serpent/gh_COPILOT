from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from assemble_db_first_bundle import HarAssetIngestor


def test_har_ingestor_creates_table_and_inserts(tmp_path: Path) -> None:
    har_file = tmp_path / "sample.har"
    har_file.write_text(json.dumps({"log": {"pages": [], "entries": []}}))
    db_path = tmp_path / "test.db"
    ingestor = HarAssetIngestor(root_dir=tmp_path, db_path=db_path)
    summary = ingestor.ingest()
    assert summary.inserted == 1
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute("SELECT file_path FROM har_entries").fetchone()
    finally:
        conn.close()
    assert row is not None and row[0].endswith("sample.har")
