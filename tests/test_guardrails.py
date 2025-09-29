import os
import tempfile

from gh_copilot.automation.guardrails import (
    guard_no_github_actions,
    guard_no_recursive_backups,
    validate_no_forbidden_paths,
)


def test_guard_no_github_actions_dry_run_passes():
    with tempfile.TemporaryDirectory() as tmp:
        w = os.path.join(tmp, ".github", "workflows")
        os.makedirs(w, exist_ok=True)
        os.environ.pop("APPLY", None)
        assert guard_no_github_actions(tmp) is True


def test_guard_no_github_actions_apply_raises():
    with tempfile.TemporaryDirectory() as tmp:
        w = os.path.join(tmp, ".github", "workflows")
        os.makedirs(w, exist_ok=True)
        with open(os.path.join(w, "some.yml"), "w", encoding="utf-8") as f:
            f.write("name: test\n")
        os.environ["APPLY"] = "1"
        try:
            raised = False
            try:
                guard_no_github_actions(tmp)
            except Exception:
                raised = True
            assert raised, "Expected guard to raise in APPLY mode"
        finally:
            os.environ.pop("APPLY", None)


def test_backup_and_forbidden_paths():
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "my_backup"))
        raised = False
        try:
            guard_no_recursive_backups(tmp)
        except Exception:
            raised = True
        assert raised, "Expected backup guard to raise"

    for p in [r"C:/temp/x", r"E:/temp/y"]:
        try:
            validate_no_forbidden_paths(p)
        except Exception:
            pass
        else:
            raise AssertionError("Expected forbidden path to raise")

    validate_no_forbidden_paths(os.getcwd())

