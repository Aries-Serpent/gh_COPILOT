import os
import socket
import time
from pathlib import Path

import requests

from copilot.orchestrators.final_enterprise_orchestrator import \
    FinalEnterpriseOrchestrator
from web_gui.app import WebGUILauncher
from web_gui_integration_system import WebGUIIntegrationSystem


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_enterprise_dashboard_launch(tmp_path):
    script = Path(__file__).resolve(
    ).parents[1] / "web_gui" / "scripts" / "flask_apps" / "enterprise_dashboard.py"
    port = get_free_port()
    os.environ["FLASK_RUN_PORT"] = str(port)
    orch = FinalEnterpriseOrchestrator(workspace_root=str(tmp_path))
    started = orch.start_service(
        "Dashboard", str(script), cwd=str(script.parent))
    try:
        assert started is True
        timeout = 10  # seconds
        interval = 0.1  # seconds
        start_time = time.time()
        while time.time() - start_time < timeout:
            healthy = orch.check_service_health("Dashboard", port=port)
            if healthy:
                break
            time.sleep(interval)
        assert healthy is True
    finally:
        proc = orch.services["Dashboard"]["process"]
        proc.terminate()
        proc.wait()
        del os.environ["FLASK_RUN_PORT"]


def test_web_gui_launcher_initializes(monkeypatch, tmp_path):
    """Ensure WebGUILauncher initializes without NameError."""
    monkeypatch.setenv("GH_COPILOT_ROOT", str(tmp_path))
    launcher = WebGUILauncher()
    assert "enterprise_dashboard" in launcher.web_components


def test_web_gui_integration_system(monkeypatch):
    """WebGUIIntegrationSystem starts dashboard and reports healthy."""
    port = get_free_port()
    monkeypatch.setenv("FLASK_RUN_PORT", str(port))
    system = WebGUIIntegrationSystem()
    system.initialize()
    try:
        resp = requests.get(f"http://localhost:{port}/api/health")
        assert resp.status_code == 200
        assert system.status()["initialized"] is True
    finally:
        system.shutdown()
        del os.environ["FLASK_RUN_PORT"]
