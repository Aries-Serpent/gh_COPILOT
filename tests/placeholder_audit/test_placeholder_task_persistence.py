from pathlib import Path
import sqlite3


def test_placeholder_task_persistence(tmp_path: Path) -> None:
    import sys
    import types

    sys.modules["dashboard.compliance_metrics_updater"] = types.SimpleNamespace(
        ComplianceMetricsUpdater=None
    )
    sys.modules["unified_script_generation_system"] = types.SimpleNamespace(
        EnterpriseUtility=None
    )
    sys.modules["quantum"] = types.ModuleType("quantum")
    sys.modules[
        "scripts.monitoring.unified_monitoring_optimization_system"
    ] = types.SimpleNamespace(
        EnterpriseUtility=object,
        push_metrics=lambda *a, **k: None,
        collect_metrics=lambda: {},
    )
    sys.modules["monitoring"] = types.ModuleType("monitoring")
    sys.modules["monitoring.health_monitor"] = types.ModuleType(
        "monitoring.health_monitor"
    )
    sys.modules["quantum_algorithm_library_expansion"] = types.ModuleType(
        "quantum_algorithm_library_expansion"
    )
    from scripts.code_placeholder_audit import log_placeholder_tasks

    db = tmp_path / "analytics.db"
    tasks = [
        {
            "task": "Remove TODO in foo.py:10 - TODO",
            "file": "foo.py",
            "line": "10",
            "pattern": "TODO",
            "context": "TODO",
            "suggestion": "fix",
        }
    ]
    inserted = log_placeholder_tasks(tasks, db, simulate=False)
    assert inserted == 1
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT file_path, line_number, pattern, context, suggestion, status FROM placeholder_tasks"
        ).fetchone()
    assert row == ("foo.py", 10, "TODO", "TODO", "fix", "open")
