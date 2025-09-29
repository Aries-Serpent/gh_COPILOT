import json
import os
import pytest
from pathlib import Path


def test_strict_schema_rejects_missing_creator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from scripts.har_ingest import main

    har = {"log": {"entries": []}}
    p = tmp_path / "s.har"; p.write_text(json.dumps(har), encoding="utf-8")
    old = os.getcwd(); os.chdir(tmp_path)
    try:
        monkeypatch.setenv("DRY_RUN", "1")
        monkeypatch.setenv("HAR_STRICT_SCHEMA", "1")
        rc = main([str(p)])
        assert rc == 1  # error captured by run_phases
    finally:
        os.chdir(old)


def test_strict_schema_off_allows_missing_creator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from scripts.har_ingest import main

    har = {"log": {"entries": []}}
    p = tmp_path / "s2.har"; p.write_text(json.dumps(har), encoding="utf-8")
    old = os.getcwd(); os.chdir(tmp_path)
    try:
        monkeypatch.setenv("DRY_RUN", "1")
        monkeypatch.delenv("HAR_STRICT_SCHEMA", raising=False)
        rc = main([str(p)])
        assert rc == 0
    finally:
        os.chdir(old)

