from __future__ import annotations

"""Guardrails to protect critical repo invariants.

Only stdlib imports are used. Functions are side-effect free in
DRY_RUN, and enforce constraints during APPLY.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List

FORBIDDEN_SUBPATHS = {
    ".github/workflows",
    ".git/hooks",
}


def _is_apply_mode() -> bool:
    """Return True when APPLY=1 in environment."""

    return os.environ.get("APPLY", "0").lower() in {"1", "true", "yes"}


def _resolve_repo_root(repo_root: str | Path | None = None) -> Path:
    """Return the resolved repository root."""

    if repo_root is not None:
        return Path(repo_root).expanduser().resolve()
    env_root = os.environ.get("GH_COPILOT_WORKSPACE")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path.cwd()


def _normalize(path: Path) -> str:
    return path.as_posix().lower()


def guard_no_github_actions(repo_root: str | Path | None = None) -> bool:
    """Prevent edits to ``.github/workflows`` in APPLY mode.

    - DRY_RUN (APPLY!=1): returns True without checks.
    - APPLY=1: if any file under ``.github/workflows`` is modified in the
      working tree, raise a ``RuntimeError``. Also blocks APPLY when preview
      workflow stubs exist under ``.codex_preview/.github/workflows``.
    """

    if not _is_apply_mode():
        return True

    root = _resolve_repo_root(repo_root)

    preview_workflows = root / ".codex_preview" / ".github" / "workflows"
    if preview_workflows.exists():
        raise RuntimeError(
            "Guard violation: preview workflows detected during APPLY mode; remove preview artifacts first."
        )

    workflows_dir = root / ".github" / "workflows"
    if not workflows_dir.exists():
        return True

    if (root / ".git").is_dir():
        try:
            proc = subprocess.run(
                ["git", "-C", str(root), "status", "--porcelain", str(workflows_dir)],
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Failed to query git status for guard checks: {exc}") from exc

        if (proc.stdout or "").strip():
            raise RuntimeError(
                "Guard violation: modifications under .github/workflows detected during APPLY."
            )
        return True

    raise RuntimeError(
        "Guard violation: .github/workflows present in APPLY mode without git context."
    )


def guard_no_recursive_backups(repo_root: str | Path | None = None) -> None:
    """Ensure backup directories/files are not nested within the repository."""

    root = _resolve_repo_root(repo_root)

    backup_root = os.environ.get("GH_COPILOT_BACKUP_ROOT")
    if backup_root:
        candidate = Path(backup_root).expanduser().resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            pass
        else:
            raise RuntimeError(
                "Guard violation: GH_COPILOT_BACKUP_ROOT must reside outside of the repository"
            )

    allow_env = os.environ.get("BACKUP_GUARD_ALLOWLIST", "")
    allow_tokens = allow_env.replace(";", ",").split(",") if allow_env else []
    allow_paths: List[Path] = []
    for raw in (token.strip() for token in allow_tokens):
        if not raw:
            continue
        try:
            allow_paths.append(Path(raw).expanduser().resolve())
        except Exception:
            continue

    def _is_allowed(candidate: Path) -> bool:
        resolved = candidate.expanduser().resolve()
        for allowed in allow_paths:
            try:
                resolved.relative_to(allowed)
            except ValueError:
                continue
            return True
        return False

    lowered = "backup"
    for path in root.rglob("*"):
        name = path.name.lower()
        if lowered in name and not _is_allowed(path):
            raise RuntimeError(f"Guard violation: backup-like path detected: {path}")


def validate_no_forbidden_paths(path: str | Path, repo_root: str | Path | None = None) -> None:
    """Ensure path is within repository and avoids forbidden segments."""

    norm_path = Path(path).expanduser().resolve()
    root = _resolve_repo_root(repo_root)

    allowlist_raw = os.environ.get("GUARD_ALLOWLIST", "")
    allowlist: List[str] = []
    for raw in (item.strip() for item in allowlist_raw.replace(";", ",").split(",")):
        if raw:
            try:
                allowlist.append(Path(raw).expanduser().resolve().as_posix().upper())
            except Exception:
                continue

    upper_norm = norm_path.as_posix().upper()
    if any(upper_norm.startswith(ok) for ok in allowlist):
        return

    forbidden_temp = {
        Path("C:/temp").resolve().as_posix().upper(),
        Path("E:/temp").resolve().as_posix().upper(),
    }
    if any(upper_norm.startswith(bad) for bad in forbidden_temp):
        raise ValueError(f"Forbidden path: {norm_path}")

    try:
        norm_path.relative_to(root)
    except ValueError as exc:
        raise ValueError("Forbidden path: escapes repository root") from exc

    normalized = _normalize(norm_path)
    for fragment in FORBIDDEN_SUBPATHS:
        if fragment in normalized:
            raise ValueError(f"Forbidden path segment detected: {norm_path}")


def validate_paths(paths: List[str], repo_root: str | Path | None = None) -> Dict[str, bool]:
    """Return pass/fail mapping for a batch of paths."""

    results: Dict[str, bool] = {}
    for p in paths:
        try:
            validate_no_forbidden_paths(p, repo_root=repo_root)
            results[p] = True
        except Exception:
            results[p] = False
    return results

