import os
import tempfile

from gh_copilot.automation.guardrails import validate_no_forbidden_paths


def test_validate_no_forbidden_paths_allows_non_forbidden():
    with tempfile.TemporaryDirectory() as tmp:
        # Ensure tmp is not in denylist
        os.environ.pop("GUARD_DENYLIST", None)
        # Should not raise
        validate_no_forbidden_paths(os.path.join(tmp, "ok"))

