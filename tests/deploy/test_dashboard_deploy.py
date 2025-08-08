import subprocess
from pathlib import Path


def test_dashboard_deploy_smoke():
    script = Path("deploy/dashboard_deploy.sh")
    result = subprocess.run(["bash", str(script)], capture_output=True, text=True, check=True)
    assert "Smoke test passed" in result.stdout
