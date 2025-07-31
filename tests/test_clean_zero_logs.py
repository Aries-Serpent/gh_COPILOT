import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "clean_zero_logs.sh"


def run_script(workdir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "logs",
        ],
        cwd=workdir,
        capture_output=True,
        text=True,
    )


def test_missing_directory(tmp_path: Path) -> None:
    result = run_script(tmp_path)
    assert result.returncode == 0
    assert "does not exist" in result.stdout


def test_cleanup(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    empty = logs / "empty.log"
    empty.touch()
    result = run_script(tmp_path)
    assert result.returncode == 0
    assert "Removed zero-size" in result.stderr
    assert not empty.exists()
    # second run should report no files
    result = run_script(tmp_path)
    assert "No zero-size" in result.stdout
