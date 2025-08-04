import os
import sys
import types

stub = types.ModuleType("scripts.correction_logger_and_rollback")
stub.CorrectionLoggerRollback = object  # type: ignore[attr-defined]
sys.modules.setdefault("scripts.correction_logger_and_rollback", stub)

import scripts.code_placeholder_audit as audit
from secondary_copilot_validator import SecondaryCopilotValidator

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"


def test_generate_removal_tasks():
    results = [{"file": "f.py", "line": 1, "pattern": "TODO", "context": "fix"}]
    tasks = audit.generate_removal_tasks(results)
    assert tasks == ["Remove TODO in f.py:1 - fix"]


def test_fail_on_findings(tmp_path, monkeypatch):
    monkeypatch.setattr(audit, "validate_results", lambda *a, **k: True)
    monkeypatch.setattr(SecondaryCopilotValidator, "validate_corrections", lambda self, files: True)
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    target = tmp_path / "demo.py"
    target.write_text("x = 1  # TODO remove\n", encoding="utf-8")
    analytics = tmp_path / "analytics.db"
    dash = tmp_path / "dashboard"
    result = audit.main(
        workspace_path=str(tmp_path),
        analytics_db=str(analytics),
        dashboard_dir=str(dash),
        simulate=True,
        fail_on_findings=True,
    )
    assert result is False
