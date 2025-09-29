import os
import tempfile

from gh_copilot.automation.guardrails import validate_no_forbidden_paths


def test_validate_no_forbidden_paths_env_denylist_blocks():
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["GUARD_DENYLIST"] = tmp
        try:
            raised = False
            try:
                validate_no_forbidden_paths(os.path.join(tmp, "x"))
            except Exception:
                raised = True
            assert raised
        finally:
            os.environ.pop("GUARD_DENYLIST", None)

