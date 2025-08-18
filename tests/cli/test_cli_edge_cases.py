from typer.testing import CliRunner
from gh_copilot.cli import app
import scripts.database.documentation_ingestor as di
import pytest
import typer

runner = CliRunner()


def test_ingest_invalid_kind():
    with pytest.raises(typer.BadParameter):
        runner.invoke(app, ["ingest", "bad"])


def test_ingest_db_error(monkeypatch, tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (tmp_path / "databases").mkdir()
    (docs_dir / "a.md").write_text("# A")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    monkeypatch.setattr(di, "enforce_anti_recursion", lambda *a, **k: None)
    monkeypatch.setattr(di, "validate_enterprise_operation", lambda *a, **k: None)
    monkeypatch.setattr(di, "get_dataset_sources", lambda *a, **k: [])
    monkeypatch.setattr(di, "log_sync_operation", lambda *a, **k: None)
    monkeypatch.setattr(di, "log_event", lambda *a, **k: None)
    monkeypatch.setattr(di, "SecondaryCopilotValidator", lambda: type("V", (), {"validate_corrections": lambda self, f: True})())

    def boom(*a, **k):
        raise RuntimeError("boom")

    monkeypatch.setattr("gh_copilot.cli._count_rows", boom)

    result = runner.invoke(app, ["ingest", "docs", "--workspace", str(tmp_path), "--src-dir", str(docs_dir)])
    assert result.exit_code == 1
