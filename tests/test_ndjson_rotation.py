import json
import os
from pathlib import Path


def test_ndjson_optional_rotation(tmp_path: Path, monkeypatch):
    from gh_copilot.automation.logging import append_ndjson

    target = tmp_path / "log.ndjson"

    # Set tiny threshold so rotation triggers before second write
    monkeypatch.setenv("NDJSON_MAX_BYTES", "1")

    rec1 = {"event": "one"}
    rec2 = {"event": "two"}

    append_ndjson(str(target), rec1)
    # After first write, no rotation yet; file exists
    assert target.exists()
    first = target.read_text(encoding="utf-8").strip()
    assert json.loads(first)["event"] == "one"

    append_ndjson(str(target), rec2)
    # Rotation happened: rotated file has first record, new file has second
    rotated = tmp_path / "log.ndjson.1"
    assert rotated.exists()
    rot_text = rotated.read_text(encoding="utf-8").strip()
    assert json.loads(rot_text)["event"] == "one"

    curr_text = target.read_text(encoding="utf-8").strip()
    assert json.loads(curr_text)["event"] == "two"

