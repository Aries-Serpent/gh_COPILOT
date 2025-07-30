import logging
import sqlite3
from scripts.optimization.enterprise_template_compliance_enhancer import EnterpriseFlake8Corrector
from secondary_copilot_validator import SecondaryCopilotValidator


def test_correct_file_logs_and_fixes(tmp_path, caplog, monkeypatch):
    bad = tmp_path / "bad.py"
    bad.write_text("import os, sys\nprint('hi')  \n", encoding="utf-8")

    called = []
    monkeypatch.setattr(
        SecondaryCopilotValidator,
        "validate_corrections",
        lambda self, files: called.append(files) or True,
    )
    events = []
    monkeypatch.setattr(
        "scripts.optimization.enterprise_template_compliance_enhancer._log_event",
        lambda evt, **kw: events.append(evt),
    )

    fixer = EnterpriseFlake8Corrector(workspace_path=str(tmp_path))
    caplog.set_level(logging.INFO)
    changed = fixer.correct_file(str(bad))

    assert called
    assert changed
    assert any(e.get("event") == "secondary_validation" for e in events)
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
        lambda evt, **kw: events.append(evt),
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
    assert any(e.get("event") == "file_corrected" for e in events)
    analytics.unlink()


def test_validation_failure_prevents_write(tmp_path, monkeypatch):
    bad = tmp_path / "bad.py"
    content = "print('hi')  \n"
    bad.write_text(content, encoding="utf-8")

    monkeypatch.setattr(
        SecondaryCopilotValidator,
        "validate_corrections",
        lambda self, files: False,
    )

    fixer = EnterpriseFlake8Corrector(workspace_path=str(tmp_path))
    changed = fixer.correct_file(str(bad))

    assert not changed
    assert bad.read_text(encoding="utf-8") == content
