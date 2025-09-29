import os
import json
import sqlite3
import pytest
from pathlib import Path


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_HAR_APPLY_TESTS", "0") != "1",
    reason="Set RUN_HAR_APPLY_TESTS=1 to run APPLY integration test",
)


def test_har_apply_integration_creates_sqlite_tables(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """APPLY integration: writes entries/pages/headers/bodies into SQLite.

    This test is opt-in to avoid side effects; set RUN_HAR_APPLY_TESTS=1.
    """
    from scripts.har_ingest import main

    # Build a minimal HAR with entries, pages, headers, bodies
    har = {
        "log": {
            "creator": {"name": "local", "version": "1"},
            "browser": {"name": "x", "version": "1"},
            "pages": [
                {"id": "page_1", "title": "Home"},
                {"id": "page_2", "title": "Next"},
            ],
            "entries": [
                {
                    "startedDateTime": "2025-01-01T00:00:00Z",
                    "request": {
                        "method": "GET",
                        "url": "http://example.com/",
                        "headers": [{"name": "X-Test", "value": "1"}],
                    },
                    "response": {
                        "status": 200,
                        "statusText": "OK",
                        "headers": [{"name": "Server", "value": "unit"}],
                        "content": {"mimeType": "text/plain", "text": "hello"},
                    },
                    "timings": {"wait": 1, "receive": 2},
                }
            ],
        }
    }

    cwd = tmp_path
    har_path = cwd / "apply.har"
    har_path.write_text(json.dumps(har), encoding="utf-8")

    # Create isolated CWD and env for APPLY
    old_cwd = os.getcwd()
    os.chdir(cwd)
    try:
        db_path = cwd / "databases" / "har_apply.db"
        # APPLY mode
        monkeypatch.setenv("DRY_RUN", "0")
        # Disable JSONL to minimize filesystem churn; focus on SQLite
        monkeypatch.setenv("HAR_PAGES_JSONL", "0")
        # No redaction by default (preserve as-is)
        monkeypatch.delenv("HAR_REDACT_HEADERS", raising=False)
        monkeypatch.delenv("HAR_REDACT_BODIES", raising=False)

        rc = main([str(har_path), "--db", str(db_path)])
        assert rc == 0

        assert db_path.exists()
        con = sqlite3.connect(str(db_path))
        try:
            cur = con.cursor()
            # entries
            cur.execute("SELECT COUNT(1) FROM har_entries")
            assert cur.fetchone()[0] == 1
            # pages
            cur.execute("SELECT COUNT(1) FROM har_pages")
            assert cur.fetchone()[0] == 2
            # headers and bodies
            cur.execute("SELECT COUNT(1) FROM har_request_headers")
            assert cur.fetchone()[0] == 1
            cur.execute("SELECT COUNT(1) FROM har_response_headers")
            assert cur.fetchone()[0] == 1
            cur.execute("SELECT COUNT(1) FROM har_request_bodies")
            # request body absent (GET), so 0
            assert cur.fetchone()[0] == 0
            cur.execute("SELECT COUNT(1) FROM har_response_bodies")
            assert cur.fetchone()[0] == 1
        finally:
            con.close()
    finally:
        os.chdir(old_cwd)

