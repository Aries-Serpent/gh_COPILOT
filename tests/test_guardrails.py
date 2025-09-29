import os
import tempfile
from pathlib import Path

import pytest

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

def test_guard_no_github_actions_preview_blocks_apply():
    with tempfile.TemporaryDirectory() as tmp:
        preview = Path(tmp) / ".codex_preview" / ".github" / "workflows"
        preview.mkdir(parents=True, exist_ok=True)
        os.environ["APPLY"] = "1"
        try:
            with pytest.raises(RuntimeError):
                guard_no_github_actions(tmp)
        finally:
            os.environ.pop("APPLY", None)


def test_backup_allowlist(tmp_path, monkeypatch):
    allowed = tmp_path / "safe_area"
    nested = allowed / "reports_backup"
    nested.mkdir(parents=True)
    monkeypatch.setenv("BACKUP_GUARD_ALLOWLIST", str(allowed))
    try:
        guard_no_recursive_backups(tmp_path)
    finally:
        monkeypatch.delenv("BACKUP_GUARD_ALLOWLIST", raising=False)


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

