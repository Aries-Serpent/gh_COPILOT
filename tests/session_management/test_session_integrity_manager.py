import importlib.util
import logging
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "utilities"
    / "SESSION_INTEGRITY_MANAGER.py"
)
spec = importlib.util.spec_from_file_location(
    "SESSION_INTEGRITY_MANAGER", MODULE_PATH
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SessionIntegrityManager = module.SessionIntegrityManager


def test_empty_database_logs_advisory(tmp_path, monkeypatch, caplog):
    (tmp_path / "empty.db").touch()
    monkeypatch.chdir(tmp_path)
    manager = SessionIntegrityManager()
    with caplog.at_level(logging.INFO):
        result = manager.validate_database_integrity()
    assert result is True
    assert any("ADVISORY" in record.message and "empty database" in record.message.lower()
               for record in caplog.records)


def test_zero_byte_cleanup_summary(tmp_path, monkeypatch, caplog):
    (tmp_path / "a.log").touch()
    (tmp_path / "b.log").touch()
    monkeypatch.chdir(tmp_path)
    manager = SessionIntegrityManager(auto_fix=True)
    with caplog.at_level(logging.INFO):
        manager.validate_file_system_integrity()
    assert any("Removed 2 zero-byte file(s)" in record.message for record in caplog.records)
    assert not any("Removed zero-byte file:" in record.message for record in caplog.records)
