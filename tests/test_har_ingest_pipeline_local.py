import io
import json
import os
from pathlib import Path


def test_normalize_handles_missing_timings():
    from scripts.har_ingest import _normalize_entry

    out = _normalize_entry({"request": {"method": "GET", "url": "http://x"}, "response": {"status": 200}})
    assert out["total_ms"] == 0.0
    assert out["status"] == 200


def test_normalize_weird_urls_tolerated():
    from scripts.har_ingest import _normalize_entry

    out1 = _normalize_entry({"request": {"method": "GET", "url": "http:///missinghost"}, "response": {"status": 200}})
    out2 = _normalize_entry({"request": {"method": "GET", "url": "http://example.com?query"}, "response": {"status": 200}})
    assert "host" in out1 and "path" in out1
    assert out2["host"].startswith("example.com")


def test_normalize_none_zero_timings_mix():
    from scripts.har_ingest import _normalize_entry

    entry = {"request": {"method": "GET", "url": "http://e/x"}, "response": {"status": 200}, "timings": {"wait": None, "receive": 5}}
    out = _normalize_entry(entry)
    assert out["total_ms"] == 5.0


def test_meta_emission_toggle(tmp_path: Path, monkeypatch):
    from scripts.har_ingest import main

    har = {"log": {"creator": {"name": "x", "version": "1"}, "browser": {"name": "b", "version": "2"}, "entries": []}}
    p = tmp_path / "meta.har"
    p.write_text(json.dumps(har), encoding="utf-8")
    old = os.getcwd()
    os.chdir(tmp_path)
    try:
        # default: off
        monkeypatch.setenv("DRY_RUN", "1")
        buf = io.StringIO(); monkeypatch.setattr("sys.stdout", buf)
        assert main([str(p)]) == 0
        text = (tmp_path / ".codex" / "action_log.ndjson").read_text(encoding="utf-8")
        assert "creator" not in text and "browser" not in text
        # on: emit meta
        monkeypatch.setenv("HAR_EMIT_META", "1")
        assert main([str(p)]) == 0
        text2 = (tmp_path / ".codex" / "action_log.ndjson").read_text(encoding="utf-8")
        assert "creator" in text2 and "browser" in text2
    finally:
        os.chdir(old)


def test_pages_preview_jsonl_written_in_dry_run(tmp_path: Path, monkeypatch):
    from scripts.har_ingest import main

    har = {"log": {"pages": [{"id": "p1"}, {"id": "p2"}], "entries": []}}
    p = tmp_path / "with_pages.har"
    p.write_text(json.dumps(har), encoding="utf-8")
    old = os.getcwd()
    os.chdir(tmp_path)
    try:
        monkeypatch.setenv("DRY_RUN", "1")
        rc = main([str(p)])
        assert rc == 0
        preview = tmp_path / ".codex" / "har_pages_preview.ndjson"
        assert preview.exists()
        lines = preview.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["id"] == "p1"
    finally:
        os.chdir(old)

