from __future__ import annotations

"""Compatibility adapter for optional Codex snapshot integration.

Import has no side effects. Call ``initialize_adapter`` to attempt loading
snapshot helpers and optionally log to NDJSON.
"""

import importlib.util
import os
from types import ModuleType
from typing import Dict, Optional


def _use_snapshot() -> bool:
    return os.environ.get("GH_COPILOT_USE_CODEX_SNAPSHOT", "0") in {"1", "true", "TRUE"}


def _default_snapshot_root() -> str:
    return os.path.join("E:/gh_COPILOT", "archive", "copied_codex_codebase")


def _try_import(path: str, name: str) -> Optional[ModuleType]:
    if not os.path.isfile(path):
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        return mod
    return None


def load_snapshot_modules(root: Optional[str] = None) -> Dict[str, ModuleType]:
    if not _use_snapshot():
        return {}
    root = root or _default_snapshot_root()
    candidates = {
        "workflow": os.path.join(root, "codex_workflow.py"),
        "task_sequence": os.path.join(root, "codex_task_sequence.py"),
    }
    loaded: Dict[str, ModuleType] = {}
    for alias, path in candidates.items():
        mod = _try_import(path, f"codex_snapshot_{alias}")
        if mod is not None:
            loaded[alias] = mod
    return loaded


def _import_stepctx_and_logger():
    try:
        from gh_copilot.automation.core import StepCtx  # type: ignore
        from gh_copilot.automation.logging import append_ndjson  # type: ignore
        return StepCtx, append_ndjson
    except Exception:
        pass
    preview_root = os.path.join(os.getcwd(), ".codex_preview", "gh_copilot")
    if os.path.isdir(preview_root):
        import sys as _sys

        _sys.path.insert(0, os.path.dirname(preview_root))
        from gh_copilot.automation.core import StepCtx  # type: ignore
        from gh_copilot.automation.logging import append_ndjson  # type: ignore

        return StepCtx, append_ndjson
    raise ImportError("gh_copilot.automation not available (live or preview)")


def make_snapshot_step(module: ModuleType, func_name: str, name: Optional[str] = None, desc: str = ""):
    StepCtx, _ = _import_stepctx_and_logger()
    fn = getattr(module, func_name)

    def _runner(*, dry_run: bool = True) -> None:
        from inspect import signature

        sig = signature(fn)
        if "dry_run" in sig.parameters:
            fn(dry_run=dry_run)
        else:
            fn()

    return StepCtx(name=name or func_name, desc=desc, fn=_runner)


def initialize_adapter(log_path: Optional[str] = None) -> Dict[str, ModuleType]:
    loaded = load_snapshot_modules()
    if log_path:
        try:
            _, append_ndjson = _import_stepctx_and_logger()
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            append_ndjson(
                log_path,
                {
                    "event": "codex_snapshot_adapter",
                    "enabled": _use_snapshot(),
                    "loaded": sorted(list(loaded.keys())),
                },
            )
        except Exception:
            pass
    return loaded

