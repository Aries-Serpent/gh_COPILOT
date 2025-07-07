import os
import time
import socket
from pathlib import Path

from copilot.orchestrators.final_enterprise_orchestrator import FinalEnterpriseOrchestrator


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_enterprise_dashboard_launch(tmp_path):
    script = Path(__file__).resolve().parents[1] / "web_gui" / "scripts" / "flask_apps" / "enterprise_dashboard.py"
    port = get_free_port()
    os.environ["FLASK_RUN_PORT"] = str(port)
    orch = FinalEnterpriseOrchestrator(workspace_root=str(tmp_path))
    started = orch.start_service("Dashboard", str(script), cwd=str(script.parent))
    try:
        assert started is True
        time.sleep(1)
        healthy = orch.check_service_health("Dashboard", port=port)
        assert healthy is True
    finally:
        proc = orch.services["Dashboard"]["process"]
        proc.terminate()
        proc.wait()
        del os.environ["FLASK_RUN_PORT"]
