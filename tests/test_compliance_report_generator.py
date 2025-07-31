from pathlib import Path
import json
import sqlite3
from validation.compliance_report_generator import generate_compliance_report


def test_generate_compliance_report(tmp_path: Path) -> None:
    ruff_file = tmp_path / "ruff.txt"
    ruff_file.write_text("file.py:1:1 F401 unused\n", encoding="utf-8")
    pytest_file = tmp_path / "pytest.json"
    pytest_file.write_text(json.dumps({"summary": {"total": 2, "passed": 2, "failed": 0}}))
    output_dir = tmp_path / "out"
    db = tmp_path / "analytics.db"
    summary = generate_compliance_report(ruff_file, pytest_file, output_dir, db)
    assert (output_dir / "compliance_report.json").exists()
    assert (output_dir / "compliance_report.md").exists()
    with sqlite3.connect(db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM code_quality_metrics")
        assert cur.fetchone()[0] == 1
    assert summary["ruff"]["issues"] == 1
