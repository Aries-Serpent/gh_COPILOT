import os
import tempfile

from gh_copilot.automation.guardrails import validate_no_forbidden_paths


def test_allowlist_precedence_over_denylist():
    with tempfile.TemporaryDirectory() as tmp:
        # Deny the tmp root, but allow a subdir explicitly
        sub = os.path.join(tmp, "safe")
        os.makedirs(sub, exist_ok=True)
        os.environ["GUARD_DENYLIST"] = tmp
        os.environ["GUARD_ALLOWLIST"] = sub
        try:
            # Subdir is allowed; should not raise
            validate_no_forbidden_paths(os.path.join(sub, "file.txt"))
        finally:
            os.environ.pop("GUARD_DENYLIST", None)
            os.environ.pop("GUARD_ALLOWLIST", None)

