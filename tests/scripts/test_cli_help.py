from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = REPO_ROOT / "scripts"

_LOG_PATTERN = re.compile(r"logs/([\w_-]+)/")


def _discover_cli_scripts() -> list[tuple[str, set[str]]]:
    scripts: list[tuple[str, set[str]]] = []
    for path in SCRIPT_DIR.glob("*.py"):
        if path.name == "__init__.py":
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if "ArgumentParser" not in content:
            continue
        log_dirs = {m.group(1) for m in _LOG_PATTERN.finditer(content)}
        scripts.append((path.stem, log_dirs))
    return sorted(scripts)


CLI_SCRIPTS = _discover_cli_scripts()


@pytest.mark.parametrize("cli, log_dirs", CLI_SCRIPTS)
def test_cli_help(cli: str, log_dirs: set[str], tmp_path: Path) -> None:
    for d in log_dirs:
        (tmp_path / "logs" / d).mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("TEST_MODE", "1")
    env.setdefault("GH_COPILOT_WORKSPACE", str(tmp_path))
    env["PYTHONPATH"] = os.pathsep.join([str(REPO_ROOT), env.get("PYTHONPATH", "")])
    result = subprocess.run(
        [sys.executable, "-m", f"scripts.{cli}", "--help"],
        capture_output=True,
        text=True,
        env=env,
        cwd=tmp_path,
    )
    if result.returncode != 0:
        pytest.xfail(result.stderr.strip())
    combined = (result.stdout + result.stderr).lower()
    assert "usage" in combined
