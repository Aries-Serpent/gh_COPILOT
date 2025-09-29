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

