import os
import json
import pytest
from pathlib import Path


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_HAR_APPLY_TESTS", "0") != "1",
    reason="Set RUN_HAR_APPLY_TESTS=1 to run APPLY JSONL entries test",
)


def test_entries_jsonl_apply(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from scripts.har_ingest import main

    har = {
        "log": {
            "entries": [
                {"request": {"method": "GET", "url": "http://a"}, "response": {"status": 200}},
                {"request": {"method": "GET", "url": "http://b"}, "response": {"status": 404}},
            ]
        }
    }
    p = tmp_path / "e.har"
    p.write_text(json.dumps(har), encoding="utf-8")

    old = os.getcwd(); os.chdir(tmp_path)
    try:
        monkeypatch.setenv("DRY_RUN", "0")
        monkeypatch.setenv("HAR_ENTRIES_JSONL", "1")
        monkeypatch.setenv("HAR_ENTRIES_JSONL_PATH", str(tmp_path / "databases" / "har_entries.ndjson"))
        monkeypatch.setenv("HAR_ENTRIES_BATCH", "1")
        rc = main([str(p)])
        assert rc == 0
        out = tmp_path / "databases" / "har_entries.ndjson"
        assert out.exists()
        lines = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines()]
        assert len(lines) == 2
        assert lines[0]["request"]["url"] == "http://a"
        assert lines[1]["response"]["status"] == 404
    finally:
        os.chdir(old)

