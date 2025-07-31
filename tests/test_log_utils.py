import pytest
from utils.log_utils import _log_event


@pytest.mark.parametrize("mode", [False, True])
def test_log_event_multiple_tables(tmp_path, monkeypatch, mode):
    if mode:
        monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")
    else:
        monkeypatch.delenv("GH_COPILOT_TEST_MODE", raising=False)

    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db = db_dir / "analytics.db"
    assert _log_event({"event": "fail", "module": "m", "level": "INFO", "target": "t1", "details": "d"}, table="rollback_failures", db_path=db, test_mode=mode)
    assert _log_event({"event": "fail2", "module": "m", "level": "INFO", "target": "t2", "details": "d2"}, table="rollback_failures", db_path=db, test_mode=mode)
    assert _log_event({"event": "fail3", "module": "m", "level": "INFO", "target": "t3", "details": "d3"}, table="rollback_failures", db_path=db, test_mode=mode)
    if mode:
        assert not db.exists()
    else:
        assert db.exists()
