from scripts.enterprise.execute_enterprise_audit import execute_enterprise_audit


def test_execute_enterprise_audit(tmp_path, monkeypatch):
    # Create minimal workspace structure
    (tmp_path / "production.db").touch()
    (tmp_path / "analytics.db").touch()
    (tmp_path / "self_healing_self_learning_system.py").touch()
    (tmp_path / "disaster_recovery").mkdir()

    gh_dir = tmp_path / ".github" / "instructions"
    gh_dir.mkdir(parents=True)
    (gh_dir / "readme.md").write_text("docs")

    (tmp_path / "sample.py").write_text("print('hi')")

    monkeypatch.chdir(tmp_path)
    results = execute_enterprise_audit()

    assert isinstance(results, dict)
    assert "enterprise_readiness" in results
    assert 0.0 <= results["enterprise_readiness"] <= 100.0
