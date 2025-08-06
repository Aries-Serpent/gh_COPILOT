import sqlite3


def test_history_and_rollback(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    from scripts import code_placeholder_audit as audit

    monkeypatch.setattr(
        "secondary_copilot_validator.SecondaryCopilotValidator.validate_corrections",
        lambda self, files: True,
    )
    monkeypatch.setattr(
        "secondary_copilot_validator.run_flake8", lambda files: None
    )
    import types
    monkeypatch.setattr(
        "scripts.code_placeholder_audit.ComplianceMetricsUpdater",
        lambda dashboard, test_mode=False: types.SimpleNamespace(
            update=lambda **kwargs: None, validate_update=lambda: None
        ),
    )
    import scripts.correction_logger_and_rollback as clr
    monkeypatch.setattr(
        clr,
        "validate_enterprise_operation",
        lambda: None,
        raising=False,
    )
    ws = tmp_path / "ws"
    ws.mkdir()
    f = ws / "a.py"
    f.write_text("# TODO x\n")

    analytics = tmp_path / "analytics.db"
    dash = tmp_path / "dash"

    audit.main(
        workspace_path=str(ws),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash),
    )

    with sqlite3.connect(analytics) as conn:
        rowid, resolved, ts = conn.execute(
            "SELECT rowid, resolved, resolved_timestamp FROM todo_fixme_tracking"
        ).fetchone()
    assert resolved == 0 and ts is None

    audit.main(
        workspace_path=str(ws),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash),
        update_resolutions=True,
    )
    with sqlite3.connect(analytics) as conn:
        r, ts = conn.execute(
            "SELECT resolved, resolved_timestamp FROM todo_fixme_tracking WHERE rowid=?",
            (rowid,),
        ).fetchone()
    assert ts is not None or r == 0

    assert audit.rollback_last_entry(analytics, rowid)
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM todo_fixme_tracking").fetchone()[0]
    assert count == 0


def test_export_option(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    from scripts import code_placeholder_audit as audit

    monkeypatch.setattr(
        "secondary_copilot_validator.SecondaryCopilotValidator.validate_corrections",
        lambda self, files: True,
    )
    import scripts.correction_logger_and_rollback as clr
    monkeypatch.setattr(
        clr,
        "validate_enterprise_operation",
        lambda: None,
        raising=False,
    )
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "b.py").write_text("# TODO y\n")
    analytics = tmp_path / "analytics.db"
    dash = tmp_path / "dash"
    export = tmp_path / "out.json"

    audit.main(
        workspace_path=str(ws),
        analytics_db=str(analytics),
        production_db=None,
        dashboard_dir=str(dash),
        simulate=True,
        export=export,
    )

    assert export.exists()
