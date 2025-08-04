from pathlib import Path

from scripts.correction_logger_and_rollback import CorrectionLoggerRollback


def test_log_change_and_validate(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    db = tmp_path / "analytics.db"
    logger = CorrectionLoggerRollback(db)
    f1 = tmp_path / "a.txt"
    f1.write_text("a", encoding="utf-8")
    logger.log_change(f1, "syntax fix", compliance_score=0.9)
    f2 = tmp_path / "b.txt"
    f2.write_text("b", encoding="utf-8")
    logger.log_change(f2, "dependency update", compliance_score=0.8)
    assert logger.validate_corrections(2)
    assert not logger.validate_corrections(3)


def test_root_cause_summarize(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    db = tmp_path / "analytics.db"
    monkeypatch.setattr(
        "scripts.correction_logger_and_rollback.DASHBOARD_DIR", tmp_path
    )
    logger = CorrectionLoggerRollback(db)
    f1 = tmp_path / "c.txt"
    f1.write_text("x", encoding="utf-8")
    logger.log_change(f1, "syntax error fix", compliance_score=0.7)
    f2 = tmp_path / "d.txt"
    f2.write_text("y", encoding="utf-8")
    logger.log_change(f2, "dependency update applied", compliance_score=0.6)
    summary = logger.summarize_corrections()
    causes = {c["root_cause"] for c in summary["corrections"]}
    assert "coding standards" in causes
    assert "dependency issue" in causes

