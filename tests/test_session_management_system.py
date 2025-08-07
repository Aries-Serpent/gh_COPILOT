import sys
import types
from types import SimpleNamespace
import pytest
import logging

sys.modules.setdefault(
    "scripts.monitoring.unified_monitoring_optimization_system",
    types.ModuleType("unified_monitoring_optimization_system"),
)
dummy_module = sys.modules["scripts.monitoring.unified_monitoring_optimization_system"]
dummy_module.EnterpriseUtility = object

import scripts.utilities.unified_session_management_system as usms


class DummyValidator:
    def __init__(self, *args, **kwargs):
        pass

    def validate_startup(self):
        return SimpleNamespace(is_success=True, errors=[], warnings=[])

    def validate_session_cleanup(self):
        # introduce a warning to trigger lesson storage
        return SimpleNamespace(is_success=True, errors=[], warnings=["cleanup warning"])


class USMSTestHarness:
    """Utility to construct a session management system with patched deps."""

    def __init__(self, monkeypatch, tmp_path):
        monkeypatch.setattr(
            "session_protocol_validator.SessionProtocolValidator",
            lambda *a, **k: DummyValidator(),
        )
        monkeypatch.setattr(
            "utils.validation_utils.validate_enterprise_environment", lambda: True
        )
        monkeypatch.setattr(
            "utils.lessons_learned_integrator.load_lessons", lambda: []
        )
        monkeypatch.setattr(
            "utils.lessons_learned_integrator.store_lesson", lambda **kwargs: None
        )
        self.system = usms.UnifiedSessionManagementSystem(workspace_root=str(tmp_path))


def test_lessons_applied_and_stored(monkeypatch, tmp_path, caplog):
    monkeypatch.setattr(
        "session_protocol_validator.SessionProtocolValidator", lambda *a, **k: DummyValidator()
    )
    monkeypatch.setattr(
        "utils.validation_utils.validate_enterprise_environment", lambda: True
    )
    monkeypatch.setattr("utils.validation_utils.detect_zero_byte_files", lambda p: [])
    monkeypatch.setattr(
        "utils.lessons_learned_integrator.load_lessons",
        lambda: [{"description": "use tmp", "tags": "session"}],
    )
    stored = []
    monkeypatch.setattr(
        "utils.lessons_learned_integrator.store_lesson",
        lambda **kwargs: stored.append(kwargs),
    )
    with caplog.at_level(logging.INFO):
        system = usms.UnifiedSessionManagementSystem(workspace_root=str(tmp_path))
        system.start_session()
        system.end_session()
    assert any("Lesson applied" in r.getMessage() for r in caplog.records)
    assert stored and stored[0]["description"] == "cleanup warning"


def test_zero_byte_file_cleanup(monkeypatch, tmp_path):
    harness = USMSTestHarness(monkeypatch, tmp_path)
    zero = tmp_path / "empty.txt"
    zero.touch()
    assert zero.exists()
    assert not harness.system.start_session()
    assert not zero.exists()


def test_scan_zero_byte_files(monkeypatch, tmp_path):
    harness = USMSTestHarness(monkeypatch, tmp_path)
    zero = tmp_path / "empty.txt"
    zero.touch()
    removed = harness.system._scan_zero_byte_files()
    assert zero not in removed or not zero.exists()
    assert removed and removed[0].name == "empty.txt"


def test_prevent_double_start(monkeypatch, tmp_path):
    harness = USMSTestHarness(monkeypatch, tmp_path)
    assert harness.system.start_session()
    with pytest.raises(RuntimeError):
        harness.system.start_session()
    assert harness.system.end_session()


def test_end_without_start(monkeypatch, tmp_path):
    harness = USMSTestHarness(monkeypatch, tmp_path)
    with pytest.raises(RuntimeError):
        harness.system.end_session()
