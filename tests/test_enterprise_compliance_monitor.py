import subprocess
from pathlib import Path

import pytest

pytest.importorskip("tqdm")

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "monitoring" / "enterprise_compliance_monitor.py"


def test_log_created(tmp_path: Path) -> None:
    subprocess.run(["python", str(SCRIPT), "--workspace", str(tmp_path), "--cycles", "1"], check=True)
    log_file = tmp_path / "logs" / "enterprise_compliance_monitor.log"
    assert log_file.exists()
    assert "Compliance monitoring complete" in log_file.read_text()
