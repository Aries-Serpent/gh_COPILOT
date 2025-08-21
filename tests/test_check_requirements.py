import subprocess
import sys
from pathlib import Path


def run_script(tmp_path: Path, content: str) -> subprocess.CompletedProcess:
    req = tmp_path / "req.txt"
    req.write_text(content)
    return subprocess.run(
        [sys.executable, "tools/check_requirements.py", str(req)],
        text=True,
        capture_output=True,
    )


def test_no_duplicates(tmp_path):
    result = run_script(tmp_path, "foo\nbar\n")
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_with_duplicates(tmp_path):
    result = run_script(tmp_path, "foo\nbar\nfoo\n")
    assert result.returncode == 1
    assert "duplicate package 'foo'" in result.stdout
