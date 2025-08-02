from pathlib import Path
import tempfile
from db_tools.operations.compliance import DatabaseComplianceChecker


def test_correct_file_removes_placeholders_and_logs():
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        (workspace / "databases").mkdir()
        checker = DatabaseComplianceChecker(workspace_path=str(workspace))
        file_path = workspace / "sample.py"
        file_path.write_text("# TODO: fix me\nprint('hi')  \n", encoding="utf-8")

        result = checker.apply_corrections([str(file_path)])
        assert str(file_path) in result
        content = file_path.read_text(encoding="utf-8")
        assert "TODO" not in content
        assert content.endswith("\n")

        rows = checker.db_connection.execute_query("SELECT success, error_message FROM corrections")
        assert rows and rows[0]["success"] == 1
        assert "removed" in rows[0]["error_message"]


def test_correct_file_failure_logged():
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        (workspace / "databases").mkdir()
        checker = DatabaseComplianceChecker(workspace_path=str(workspace))
        missing_file = workspace / "missing.py"

        result = checker.apply_corrections([str(missing_file)])
        assert str(missing_file) not in result
        rows = checker.db_connection.execute_query("SELECT success, error_message FROM corrections")
        assert rows and rows[0]["success"] == 0
        assert rows[0]["error_message"]
