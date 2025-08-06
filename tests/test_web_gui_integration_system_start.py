def test_start_invokes_integrator_and_app_run(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    from scripts.utilities import web_gui_integration_system as module

    system = module.WebGUIIntegrationSystem()
    called = {"register": False, "initialize": False, "port": None}

    def fake_register(app):
        assert app is module.app
        called["register"] = True

    def fake_initialize():
        called["initialize"] = True

    def fake_run(*, port, **kwargs):
        called["port"] = port

    monkeypatch.setattr(system.integrator, "register_endpoints", fake_register)
    monkeypatch.setattr(system.integrator, "initialize", fake_initialize)
    monkeypatch.setattr(module.app, "run", fake_run)

    system.start(port=1234)

    assert called == {"register": True, "initialize": True, "port": 1234}
