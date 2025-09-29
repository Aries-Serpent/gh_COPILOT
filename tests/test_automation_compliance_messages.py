import json
import sqlite3
from pathlib import Path

from gh_copilot.automation.core import ExecutionResult, persist_messages_to_compliance
from scripts.compliance.update_compliance_metrics import _ensure_metrics_table


def _make_row(tmp_path: Path) -> tuple[Path, int]:
    db_path = tmp_path / "analytics.db"
    with sqlite3.connect(db_path) as conn:
        _ensure_metrics_table(conn)
        conn.execute(
            """
            INSERT INTO compliance_metrics_history (
                ts, ruff_issues, tests_passed, tests_total,
                placeholders_open, placeholders_resolved,
                sessions_successful, sessions_failed,
                lint_score, test_score, placeholder_score, session_score,
                composite_score, source, meta_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                100.0,
                100.0,
                100.0,
                100.0,
                100.0,
                "test",
                json.dumps({"existing": True}),
            ),
        )
        conn.commit()
        row_id = conn.execute(
            "SELECT id FROM compliance_metrics_history ORDER BY id DESC LIMIT 1"
        ).fetchone()[0]
    return db_path, int(row_id)


def test_persist_messages_updates_meta_json(tmp_path):
    db_path, row_id = _make_row(tmp_path)
    result = ExecutionResult(
        phases_completed=2,
        ok=True,
        logs=[],
        messages=["done:A:dry_run", "skip:B:dry_run_blocked"],
    )

    persist_messages_to_compliance(
        result,
        workspace=str(tmp_path),
        db_path=db_path,
        row_id=row_id,
    )

    with sqlite3.connect(db_path) as conn:
        payload = conn.execute(
            "SELECT meta_json FROM compliance_metrics_history WHERE id=?",
            (row_id,),
        ).fetchone()[0]
    data = json.loads(payload)
    assert data.get("existing") is True
    automation = data.get("automation_messages")
    assert automation
    assert automation["message_total"] == 2
    assert automation["messages"][0] == "done:A:dry_run"
    assert automation["truncated"] is False
