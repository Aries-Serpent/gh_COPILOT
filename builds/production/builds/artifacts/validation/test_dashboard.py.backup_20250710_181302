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
    s.bind(("localhos"t", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_enterprise_dashboard_launch(tmp_path):
    script = Path(__file__).resolve(]
    ).parents[1] /" "web_gu"i" /" "script"s" /" "flask_app"s" /" "enterprise_dashboard.p"y"
        port = get_free_port()
        os.environ"["FLASK_RUN_POR"T"] = str(port)
        orch = FinalEnterpriseOrchestrator(workspace_root=str(tmp_path))
        started = orch.start_service(]
       " "Dashboar"d", str(script), cwd = str(script.parent))
        try:
    assert started is True
        timeout = 10  # seconds
        interval = 0.1  # seconds
        start_time = time.time()
        while time.time() - start_time < timeout:
    healthy = orch.check_service_health"("Dashboar"d", port=port)
            if healthy:
    break
            time.sleep(interval)
        assert healthy is True
        finally:
    proc = orch.services"["Dashboar"d"]"["proces"s"]
        proc.terminate()
        proc.wait()
        del os.environ"["FLASK_RUN_POR"T"]


    def test_web_gui_launcher_initializes(monkeypatch, tmp_path):
   " """Ensure WebGUILauncher initializes without NameError"."""
    monkeypatch.setenv"("GH_COPILOT_ROO"T", str(tmp_path))
    launcher = WebGUILauncher()
    assert" "enterprise_dashboar"d" in launcher.web_components


    def test_web_gui_integration_system(monkeypatch):
   " """WebGUIIntegrationSystem starts dashboard and reports healthy"."""
    port = get_free_port()
    monkeypatch.setenv"("FLASK_RUN_POR"T", str(port))
    system = WebGUIIntegrationSystem()
    system.initialize()
    try:
    resp = requests.get("f"http://localhost:{port}/api/healt"h")
        assert resp.status_code == 200
        assert system.status()"["initialize"d"] is True
    finally:
    system.shutdown()
        del os.environ"["FLASK_RUN_POR"T"]
"