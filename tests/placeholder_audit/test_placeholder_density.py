import sqlite3
import sys
import types
from pathlib import Path

sys.modules.setdefault(
    "dashboard.compliance_metrics_updater", types.SimpleNamespace(ComplianceMetricsUpdater=None)
)
sys.modules.setdefault(
    "unified_monitoring_optimization_system",
    types.SimpleNamespace(
        EnterpriseUtility=None,
        push_metrics=lambda *a, **k: None,
        collect_metrics=lambda *a, **k: None,
    ),
)

from scripts.code_placeholder_audit import calculate_placeholder_density


def test_placeholder_density_alert(tmp_path, caplog):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    file = workspace / "a.py"
    file.write_text("x=1\n" * 1000)
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE placeholder_tasks (file_path TEXT, line_number INTEGER, pattern TEXT, context TEXT, status TEXT)"
        )
        for i in range(6):
            conn.execute(
                "INSERT INTO placeholder_tasks VALUES ('a.py', ?, 'TODO', '', 'open')",
                (i,),
            )
        conn.commit()
    with caplog.at_level("WARNING"):
        density = calculate_placeholder_density(db, workspace)
    assert density > 5
    assert any("Placeholder density" in r.message for r in caplog.records)
    with sqlite3.connect(db) as conn:
        val = conn.execute("SELECT density FROM placeholder_density").fetchone()[0]
    assert val == density

