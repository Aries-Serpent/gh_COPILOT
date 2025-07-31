import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_zero_logs.sh"


def run_script(workdir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(SCRIPT), "logs"], cwd=workdir, capture_output=True, text=True)


def test_missing_directory(tmp_path: Path) -> None:
    result = run_script(tmp_path)
    assert result.returncode == 0
    assert "does not exist" in result.stdout


def test_zero_byte_detection(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "empty.log").touch()
    result = run_script(tmp_path)
    assert result.returncode == 1
    assert "Zero-size" in result.stderr
    (logs / "empty.log").unlink()
    result = run_script(tmp_path)
    assert result.returncode == 0
    assert "No zero-size" in result.stdout
