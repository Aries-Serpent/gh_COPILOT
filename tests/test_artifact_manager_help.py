from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_help_lists_all_options() -> None:
    script = Path(__file__).resolve().parents[1] / "artifact_manager.py"
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    help_text = result.stdout
    options = {
        "--package": "create a session archive",
        "--recover": "restore the most recent session archive",
        "--commit": "commit the created archive",
        "--message": "commit message",
        "--tmp-dir": "working directory for session files",
        "--sync-gitattributes": "regenerate .gitattributes",
    }
    for opt, snippet in options.items():
        assert opt in help_text
        assert snippet in help_text
