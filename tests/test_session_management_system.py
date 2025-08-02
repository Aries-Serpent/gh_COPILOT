import logging
from types import SimpleNamespace

import scripts.utilities.unified_session_management_system as usms


class DummyValidator:
    def __init__(self, *args, **kwargs):
        pass

    def validate_startup(self):
        return SimpleNamespace(is_success=True, errors=[], warnings=[])

    def validate_session_cleanup(self):
        # introduce a warning to trigger lesson storage
        return SimpleNamespace(is_success=True, errors=[], warnings=["cleanup warning"])


def test_lessons_applied_and_stored(monkeypatch, tmp_path, caplog):
    monkeypatch.setattr(usms, "SessionProtocolValidator", lambda *a, **k: DummyValidator())
    monkeypatch.setattr(usms, "validate_enterprise_environment", lambda: True)
    monkeypatch.setattr(usms, "detect_zero_byte_files", lambda p: [])
    monkeypatch.setattr(usms, "load_lessons", lambda: [{"description": "use tmp", "tags": "session"}])
    stored = []
    monkeypatch.setattr(usms, "store_lesson", lambda **kwargs: stored.append(kwargs))
    with caplog.at_level(logging.INFO):
        system = usms.UnifiedSessionManagementSystem(workspace_root=str(tmp_path))
        system.start_session()
        system.end_session()
    assert any("Lesson applied" in r.getMessage() for r in caplog.records)
    assert stored and stored[0]["description"] == "cleanup warning"
