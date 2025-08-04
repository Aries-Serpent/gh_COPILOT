from unified_disaster_recovery_system import UnifiedDisasterRecoverySystem


def test_disaster_recovery_instantiation(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    system = UnifiedDisasterRecoverySystem(str(tmp_path))
    assert system.workspace_path == tmp_path


def test_web_gui_instantiation(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    from web_gui_integration_system import WebGUIIntegrationSystem

    system = WebGUIIntegrationSystem()
    assert system.db_path.parent.name == "databases"
