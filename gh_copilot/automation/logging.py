from __future__ import annotations

"""NDJSON logging helper with best-effort atomic append.

Writes to the provided file path. If DRY_RUN is active (default) and APPLY is
not enabled, entries are routed into ``.codex_preview`` to avoid mutating live
artifacts. Append is implemented by rewriting a temp file then replacing the
original to minimize partial writes.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict


def _resolve_root() -> Path:
    workspace = os.environ.get("GH_COPILOT_WORKSPACE")
    if workspace:
        return Path(workspace).expanduser().resolve()
    return Path.cwd()


def _resolve_target(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = (_resolve_root() / candidate).resolve()
    return candidate


def append_ndjson(path: str | Path, record: Dict[str, Any]) -> Path:
    """Append a record as one JSON line to ``path``.

    Returns the resolved path that received the write. When DRY_RUN is active
    (``DRY_RUN=1`` or unset) and APPLY is not enabled, the write is redirected
    into ``.codex_preview`` under the same relative location.
    """

    target = _resolve_target(path)
    dry_run = os.environ.get("APPLY", "0") != "1" and os.environ.get("DRY_RUN", "1") != "0"
    if dry_run:
        root = _resolve_root()
        try:
            relative = target.relative_to(root)
        except ValueError:
            relative = Path(target.name)
        target = (root / ".codex_preview" / relative).resolve()

    target.parent.mkdir(parents=True, exist_ok=True)

    new_line = json.dumps(record, ensure_ascii=False) + "\n"

    try:
        max_bytes = int(os.environ.get("NDJSON_MAX_BYTES", "0"))
    except ValueError:
        max_bytes = 0

    if max_bytes > 0 and target.exists() and target.stat().st_size >= max_bytes:
        rotated = target.with_suffix(target.suffix + ".1")
        try:
            target.replace(rotated)
        except Exception:
            try:
                if rotated.exists():
                    rotated.unlink()
                target.rename(rotated)
            except Exception:
                pass

    temp_dir = target.parent if target.parent.exists() else None
    fd, tmp = tempfile.mkstemp(prefix="ndjson_", suffix=".tmp", dir=temp_dir)
    tmp_path = Path(tmp)
    try:
        if target.exists():
            with target.open("r", encoding="utf-8", errors="replace") as src:
                existing = src.read()
        else:
            existing = ""
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            if existing:
                handle.write(existing)
            handle.write(new_line)
        tmp_path.replace(target)
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass

    return target
