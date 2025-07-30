import logging
import sqlite3
from pathlib import Path
from scripts.optimization.enterprise_template_compliance_enhancer import EnterpriseFlake8Corrector


def test_correct_file_logs_and_fixes(tmp_path, caplog):
    bad = tmp_path / "bad.py"
    bad.write_text("import os, sys\nprint('hi')  \n", encoding="utf-8")

    fixer = EnterpriseFlake8Corrector(workspace_path=str(tmp_path))
    caplog.set_level(logging.INFO)
    changed = fixer.correct_file(str(bad))

    assert changed
    assert bad.read_text(encoding="utf-8") == "import os\nimport sys\n\nprint('hi')\n"
    assert any("SUCCESS" in record.message for record in caplog.records)


def test_correct_file_updates_tracking(tmp_path, monkeypatch):
    bad = tmp_path / "bad.py"
    bad.write_text("print('hi')  \n", encoding="utf-8")
    analytics = tmp_path / "databases" / "analytics.db"
    analytics.parent.mkdir(parents=True)
    with sqlite3.connect(analytics) as conn:
        conn.execute("CREATE TABLE todo_fixme_tracking (file_path TEXT, resolved INTEGER, resolved_timestamp TEXT)")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (?,0,NULL)", (str(bad),))

    events = []
    monkeypatch.setattr(
        "scripts.optimization.enterprise_template_compliance_enhancer._log_event",
        lambda evt, **kw: events.append((kw.get("table"), evt)),
    )
    fixer = EnterpriseFlake8Corrector(workspace_path=str(tmp_path))
    fixer.analytics_db = analytics
    assert fixer.correct_file(str(bad))
    with sqlite3.connect(analytics) as conn:
        resolved = conn.execute(
            "SELECT resolved FROM todo_fixme_tracking WHERE file_path=?",
            (str(bad),),
        ).fetchone()[0]
    assert resolved == 1
    assert any(t == "correction_logs" for t, _ in events)
    with sqlite3.connect(analytics) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM correction_logs WHERE file_path=?",
            (str(bad),),
        ).fetchone()[0]
    assert count == 1
    analytics.unlink()
