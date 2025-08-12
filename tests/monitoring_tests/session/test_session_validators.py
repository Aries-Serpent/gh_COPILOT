from __future__ import annotations

from pathlib import Path

from ghc_monitoring.session_validators import (
    find_open_handles,
    log_is_complete,
    validate_session,
)


def test_find_open_handles_detects_unclosed_file(tmp_path):
    target = tmp_path / "data.txt"
    handle = open(target, "w")
    handle.write("x")
    handle.flush()
    try:
        open_files = find_open_handles(tmp_path)
        assert any(Path(p) == target for p in open_files)
    finally:
        handle.close()


def test_log_is_complete_and_validate_session(tmp_path):
    log_file = tmp_path / "session.log"
    log_file.write_text("START\n")
    handle = open(tmp_path / "temp.txt", "w")
    handle.write("temp")
    handle.flush()
    try:
        errors = validate_session(log_file)
        assert any("open handles" in e for e in errors)
        assert any("incomplete log" in e for e in errors)
    finally:
        handle.close()

    log_file.write_text("START\nSHUTDOWN COMPLETE\n")
    assert log_is_complete(log_file)
    assert validate_session(log_file) == []
