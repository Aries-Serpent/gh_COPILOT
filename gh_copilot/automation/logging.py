from __future__ import annotations

"""NDJSON logging helper with best-effort atomic append.

Writes to the provided file path. If the file does not exist, it is created.
Append is implemented by rewriting a temp file then replacing the target to
minimize partial writes.
"""

import json
import os
import tempfile
from typing import Any, Dict


def append_ndjson(path: str, record: Dict[str, Any]) -> None:
    """Append a record as one JSON line to ``path``.

    The parent directory is created if missing. The write uses a temp file and
    ``os.replace`` to avoid torn writes.
    """

    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    new_line = json.dumps(record, ensure_ascii=False) + "\n"

    # Optional rotation: if NDJSON_MAX_BYTES is set (>0) and the target file
    # exceeds the threshold, rotate to <path>.1 and start a new file.
    try:
        max_bytes = int(os.environ.get("NDJSON_MAX_BYTES", "0"))
    except ValueError:
        max_bytes = 0
    if max_bytes > 0 and os.path.exists(path):
        try:
            if os.path.getsize(path) >= max_bytes:
                rotated = path + ".1"
                try:
                    os.replace(path, rotated)
                except Exception:
                    try:
                        if os.path.exists(rotated):
                            os.remove(rotated)
                        os.rename(path, rotated)
                    except Exception:
                        # proceed without rotation if filesystem disallows
                        pass
        except Exception:
            # ignore rotation errors
            pass

    if not os.path.exists(path):
        fd, tmp = tempfile.mkstemp(prefix="ndjson_", suffix=".tmp", dir=parent or None)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(new_line)
            os.replace(tmp, path)
        finally:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except OSError:
                pass
        return

    fd, tmp = tempfile.mkstemp(prefix="ndjson_", suffix=".tmp", dir=parent or None)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as src:
            existing = src.read()
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if existing:
                f.write(existing)
            f.write(new_line)
        os.replace(tmp, path)
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass
