import sqlite3
from pathlib import Path
import types
import sys
import pytest
try:
    import numpy  # noqa: F401
except Exception:
    pytest.skip("numpy not available", allow_module_level=True)


def test_enterprise_utility_logs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "0")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "bk"))
    (tmp_path / "databases").mkdir()
    db_file = tmp_path / "databases" / "analytics.db"
    class DummyTqdm:
        def __init__(self, *a, **k):
            pass
        def update(self, *a, **k):
            pass
        def set_postfix_str(self, *a, **k):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *a, **k):
            return False
    sys.modules['tqdm'] = types.SimpleNamespace(tqdm=DummyTqdm)
    import unified_session_management_system as usm
    monkeypatch.setattr(usm, "ANALYTICS_DB", db_file)
    from session_management_consolidation_executor import EnterpriseUtility
    util = EnterpriseUtility(str(tmp_path))
    assert util.execute_utility()
    db = tmp_path / "databases" / "analytics.db"
    with sqlite3.connect(db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM event_log WHERE event='utility_start'").fetchone()[0]
    assert count == 1
