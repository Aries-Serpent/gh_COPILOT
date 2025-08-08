from pathlib import Path
import subprocess


def test_dashboard_deploy_runs(tmp_path):
    script = Path("deploy/dashboard_deploy.sh")
    result = subprocess.run(["bash", str(script)], capture_output=True, text=True, check=True)
    out = result.stdout
    assert "[1/4] Building dashboard image" in out
    assert "[2/4] Running database migrations" in out
    assert "[3/4] Starting dashboard service" in out
    assert "[4/4] Running smoke tests for" in out
    assert "WebSocket port" in out
