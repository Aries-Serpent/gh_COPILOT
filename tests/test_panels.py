
# Auto-generated integration test (lightweight)
def test_panel_update_js_presence():
    import pathlib

    panels = [
        pathlib.Path("codex_changes/stubs/templates/compliance_panel.html"),
        pathlib.Path("codex_changes/stubs/templates/monitoring_panel.html"),
        pathlib.Path("codex_changes/stubs/templates/synchronization_panel.html"),
    ]
    for p in panels:
        if p.exists():
            s = p.read_text(encoding="utf-8", errors="ignore")
            assert "function updateGauges" in s
