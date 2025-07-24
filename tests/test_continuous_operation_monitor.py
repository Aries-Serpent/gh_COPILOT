import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "monitoring" / "continuous_operation_monitor.py"


def test_log_created(tmp_path: Path) -> None:
    subprocess.run(["python", str(SCRIPT), "--workspace", str(tmp_path), "--iterations", "1"], check=True)
    log_file = tmp_path / "logs" / "continuous_operation_monitor.log"
    assert log_file.exists()
    assert "Continuous monitoring complete" in log_file.read_text()
