from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_help_mentions_policy_and_examples() -> None:
    script = Path(__file__).resolve().parents[1] / "artifact_manager.py"
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    help_text = result.stdout
    option_snippets = {
        "--package": [".codex_lfs_policy.yaml", "--package --tmp-dir /custom/tmp"],
        "--recover": [".codex_lfs_policy.yaml", "--recover --tmp-dir /custom/tmp"],
        "--commit": [".codex_lfs_policy.yaml", "--package --commit"],
        "--message": [".codex_lfs_policy.yaml", "--message 'Add session artifacts'"],
        "--tmp-dir": [".codex_lfs_policy.yaml", "--tmp-dir /custom/tmp"],
        "--sync-gitattributes": [".codex_lfs_policy.yaml", "--sync-gitattributes"],
    }
    for opt, snippets in option_snippets.items():
        assert opt in help_text
        for snippet in snippets:
            assert snippet in help_text
