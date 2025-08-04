def test_main_invokes_start(monkeypatch, tmp_path):
    from scripts.utilities.web_gui_integration_system import WebGUIIntegrationSystem
    from web_gui_integration_system import main

    calls = {}

    def fake_start(self, port=5000):
        calls["port"] = port

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(WebGUIIntegrationSystem, "start", fake_start)

    assert main() == 0
    assert calls["port"] == 5000
