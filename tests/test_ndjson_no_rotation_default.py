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



def test_append_ndjson_routes_to_preview(tmp_path, monkeypatch):
    from gh_copilot.automation.logging import append_ndjson

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.delenv("APPLY", raising=False)
    monkeypatch.delenv("DRY_RUN", raising=False)

    preview_path = append_ndjson(".codex/action_log.ndjson", {"event": "preview"})

    expected = (tmp_path / ".codex_preview" / ".codex" / "action_log.ndjson").resolve()
    assert preview_path == expected
    assert expected.exists()
    assert not (tmp_path / ".codex" / "action_log.ndjson").exists()
    data = expected.read_text(encoding="utf-8").strip()
    assert data
