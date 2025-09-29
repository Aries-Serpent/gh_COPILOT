import json
from pathlib import Path


def test_ndjson_no_rotation_when_disabled(tmp_path: Path, monkeypatch):
    from gh_copilot.automation.logging import append_ndjson

    # Ensure rotation disabled
    monkeypatch.delenv("NDJSON_MAX_BYTES", raising=False)

    target = tmp_path / "plain.ndjson"
    append_ndjson(str(target), {"n": 1})
    append_ndjson(str(target), {"n": 2})

    # No rotated file should exist
    assert not (tmp_path / "plain.ndjson.1").exists()

    lines = [json.loads(l) for l in target.read_text(encoding="utf-8").splitlines()]
    assert [l["n"] for l in lines] == [1, 2]

