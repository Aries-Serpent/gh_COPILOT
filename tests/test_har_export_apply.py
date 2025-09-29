import json
import os
import sqlite3
import pytest
from pathlib import Path


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_HAR_APPLY_TESTS", "0") != "1",
    reason="Set RUN_HAR_APPLY_TESTS=1 to run APPLY export test",
)


def test_har_export_jsonl_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from scripts.har_ingest import main as ingest_main
    from scripts.har_export import main as export_main

    # Create small DB via APPLY ingest
    har = {
        "log": {
            "entries": [
                {
                    "request": {"method": "GET", "url": "http://x", "headers": [{"name": "A", "value": "1"}]},
                    "response": {"status": 200, "headers": [{"name": "B", "value": "2"}], "content": {"text": "ok", "mimeType": "text/plain"}},
                }
            ],
            "pages": [{"id": "p1"}],
        }
    }
    har_path = tmp_path / "mini.har"
    har_path.write_text(json.dumps(har), encoding="utf-8")

    old = os.getcwd(); os.chdir(tmp_path)
    try:
        monkeypatch.setenv("DRY_RUN", "0")
        db_path = tmp_path / "databases" / "mini.db"
        assert ingest_main([str(har_path), "--db", str(db_path)]) == 0
        out_dir = tmp_path / "exports"
        assert export_main(["--db", str(db_path), "--out", str(out_dir)]) == 0
        # Validate JSONL files exist and have at least one line where applicable
        expect = [
            "har_entries.ndjson",
            "har_pages.ndjson",
            "har_request_headers.ndjson",
            "har_response_headers.ndjson",
            "har_response_bodies.ndjson",
        ]
        for name in expect:
            p = out_dir / name
            assert p.exists()
            assert p.read_text(encoding="utf-8").strip()
        # request bodies absent for GET
        assert not (out_dir / "har_request_bodies.ndjson").exists() or not (out_dir / "har_request_bodies.ndjson").read_text(encoding="utf-8").strip()
    finally:
        os.chdir(old)

