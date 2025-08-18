import json
import sqlite3
from types import SimpleNamespace

from typer.testing import CliRunner
import typer

from gh_copilot.cli import app, _count_rows, compute_score

runner = CliRunner()


def test_migrate_cli(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    monkeypatch.setenv("GH_COPILOT_ANALYTICS_DB", str(db))
    mig = tmp_path / "migs"
    mig.mkdir()
    (mig / "001.sql").write_text("CREATE TABLE t(id INTEGER);")

    result = runner.invoke(app, ["migrate", "--migrations-dir", str(mig)])
    assert result.exit_code == 0
    assert "applied:" in result.stdout
    assert _count_rows(db, "t") == 0


def test_migrate_all_cli(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    monkeypatch.setenv("GH_COPILOT_ANALYTICS_DB", str(db))
    mig = tmp_path / "migs"
    mig.mkdir()
    (mig / "001.sql").write_text("CREATE TABLE t(id INTEGER);")
    (mig / "002.py").write_text("def upgrade(conn):\n    conn.execute('CREATE TABLE u(id INTEGER)')\n")

    result = runner.invoke(app, ["migrate-all", "--migrations-dir", str(mig)])
    assert result.exit_code == 0
    assert "applied: 001.sql" in result.stdout
    assert "applied: 002.py" in result.stdout


def test_seed_models_cli(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    monkeypatch.setenv("GH_COPILOT_ANALYTICS_DB", str(db))
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE compliance_models(model_id TEXT PRIMARY KEY, weights_json TEXT, min_score REAL, effective_from TEXT)"
    )
    conn.commit()
    conn.close()

    result = runner.invoke(app, ["seed-models"])
    assert result.exit_code == 0
    assert "seeded default models" in result.stdout
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT COUNT(*) FROM compliance_models").fetchone()[0]
    conn.close()
    assert rows == 2


def test_compute_score_cli(monkeypatch, capsys):
    calls: list[tuple] = []
    import sys
    import types

    class DummyDAO:
        class Model(SimpleNamespace):
            model_id = "m"
            lint = tests = placeholders = sessions = 1.0

        def fetch_active_model(self, branch):  # noqa: D401 - simple stub
            return self.Model()

        def store_score_inputs(self, inputs):
            calls.append(("inputs", inputs))

        def store_score_snapshot(self, snap):
            calls.append(("snap", snap))

    stub_models = types.SimpleNamespace(
        ScoreInputs=lambda **k: SimpleNamespace(**k),
        ScoreSnapshot=lambda **k: SimpleNamespace(**k),
    )
    monkeypatch.setitem(sys.modules, "gh_copilot.models", stub_models)
    monkeypatch.setattr("gh_copilot.cli._dao", DummyDAO())

    compute_score(lint=1, tests=1, placeholders=1, sessions=1)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["score"] == 4
    assert len(calls) == 2


def test_ingest_invalid_kind_cli(tmp_path):
    import pytest

    with pytest.raises(typer.BadParameter):
        runner.invoke(app, ["ingest", "bad", "--workspace", str(tmp_path)])


def test_generate_cli(tmp_path, monkeypatch):
    out = tmp_path / "out"
    out.mkdir()
    monkeypatch.setenv("GH_COPILOT_ANALYTICS_DB", str(tmp_path / "a.db"))

    def _gen(**kwargs):
        return [out / "a.txt"]

    monkeypatch.setattr("gh_copilot.generation.generate_from_templates.generate", _gen)

    result = runner.invoke(
        app,
        ["generate", "docs", "--source-db", str(tmp_path / "s.db"), "--out-dir", str(out), "--params", "{}"],
    )
    assert result.exit_code == 0
    assert "a.txt" in result.stdout


def test_audit_consistency_cli(tmp_path, monkeypatch):
    def _run(*a, **k):
        return SimpleNamespace(found=1)

    monkeypatch.setattr("gh_copilot.auditor.consistency.run_audit", _run)

    result = runner.invoke(app, ["audit-consistency"])
    assert result.exit_code == 0
    assert "found" in result.stdout


def test_count_rows_cache(monkeypatch, tmp_path):
    db = tmp_path / "x.db"
    calls = {"n": 0}
    orig = sqlite3.connect

    def fake_connect(path):
        calls["n"] += 1
        return orig(path)

    monkeypatch.setattr(sqlite3, "connect", fake_connect)
    assert _count_rows(db, "t") == 0
    assert _count_rows(db, "t") == 0
    assert calls["n"] == 1


def test_serve_cli(monkeypatch):
    called = {}
    import sys
    import types

    def fake_run(app_str, host, port, reload):
        called["args"] = (app_str, host, port, reload)

    stub_uvicorn = types.SimpleNamespace(run=fake_run)
    monkeypatch.setitem(sys.modules, "uvicorn", stub_uvicorn)

    serve_host = "0.0.0.0"
    result = runner.invoke(app, ["serve", "--host", serve_host, "--port", "1234"])
    assert result.exit_code == 0
    assert called["args"] == ("gh_copilot.api:app", serve_host, "1234", True)
