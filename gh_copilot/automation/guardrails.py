from __future__ import annotations

"""Guardrails to protect critical repo invariants.

Only stdlib imports are used. Functions are side-effect free in
DRY_RUN, and enforce constraints during APPLY.
"""

import os
import subprocess
from typing import Dict, List


def _is_apply_mode() -> bool:
    """Return True when APPLY=1 in environment."""

    return os.environ.get("APPLY", "0") in {"1", "true", "TRUE", "yes", "YES"}


def guard_no_github_actions(repo_root: str) -> bool:
    """Prevent edits to ``.github/workflows`` in APPLY mode.

    - DRY_RUN (APPLY!=1): returns True without checks.
    - APPLY=1: if any file under ``.github/workflows`` is modified in the
      working tree, raise a ``RuntimeError``.

    Returns True if no violations are detected.
    """

    if not _is_apply_mode():
        return True

    workflows_dir = os.path.join(repo_root, ".github", "workflows")
    if not os.path.isdir(workflows_dir):
        return True

    git_dir = os.path.join(repo_root, ".git")
    if os.path.isdir(git_dir):
        try:
            proc = subprocess.run(
                ["git", "-C", repo_root, "status", "--porcelain", ".github/workflows"],
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Failed to query git status for guard checks: {exc}")

        changed = (proc.stdout or "").strip()
        if changed:
            raise RuntimeError(
                "Guard violation: modifications under .github/workflows detected during APPLY."
            )
        return True

    # Fallback: not a git repo — presence of workflows directory + APPLY=1 is a violation
    raise RuntimeError(
        "Guard violation: .github/workflows present in APPLY mode without git context."
    )


def guard_no_recursive_backups(repo_root: str) -> None:
    """Scan for directories/files indicating backup recursion under repo root.

    Any path component containing 'backup' (case-insensitive) triggers a
    violation. Intended to prevent storing backups inside the workspace.
    """

    lowered = "backup"
    for dirpath, dirnames, filenames in os.walk(repo_root):
        base = os.path.basename(dirpath)
        if lowered in base.lower():
            raise RuntimeError(
                f"Guard violation: backup-like directory detected: {dirpath}"
            )
        for d in dirnames:
            if lowered in d.lower():
                raise RuntimeError(
                    f"Guard violation: backup-like directory detected: {os.path.join(dirpath, d)}"
                )
        for f in filenames:
            if lowered in f.lower():
                raise RuntimeError(
                    f"Guard violation: backup-like file detected: {os.path.join(dirpath, f)}"
                )


def validate_no_forbidden_paths(path: str) -> None:
    """Ensure path does not target forbidden temp locations.

    Specifically blocks writes to ``C:/temp`` and ``E:/temp`` (case-insensitive).
    """

    norm = os.path.abspath(path)
    upper = norm.replace("/", os.sep).replace("\\", os.sep).upper()
    forbidden = {
        os.path.abspath(os.path.join("C:" + os.sep, "temp")).upper(),
        os.path.abspath(os.path.join("E:" + os.sep, "temp")).upper(),
    }
    # Optional allowlist (absolute prefixes) takes precedence over denylist
    allowlist_raw = os.environ.get("GUARD_ALLOWLIST", "")
    allowlist = []
    for raw in [p.strip() for p in allowlist_raw.replace(";", ",").split(",") if p.strip()]:
        try:
            allowlist.append(os.path.abspath(raw).upper())
        except Exception:
            continue
    for bad in forbidden:
        if upper.startswith(bad):
            # If explicitly allowed, skip error
            for ok in allowlist:
                if upper.startswith(ok):
                    return
            raise ValueError(f"Forbidden path: {path}")


def validate_paths(paths: List[str]) -> Dict[str, bool]:
    """Return pass/fail mapping for a batch of paths.

    This helper does not raise; it returns a dict {path: True/False} using
    validate_no_forbidden_paths semantics (allowlist precedence, then denylist).
    """
    results: Dict[str, bool] = {}
    for p in paths:
        try:
            validate_no_forbidden_paths(p)
            results[p] = True
        except Exception:
            results[p] = False
    return results
