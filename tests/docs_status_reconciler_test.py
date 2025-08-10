"""Tests for docs_status_reconciler."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import docs_status_reconciler as reconciler


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_reconcile_success(tmp_path: Path) -> None:
    phase5 = _write(
        tmp_path / "PHASE5_TASKS_STARTED.md",
        """
## 1. TaskA
- [x] **Progress:** 100%
""".strip(),
    )
    stubs = _write(
        tmp_path / "task_stubs.md",
        """
| Task | Design | Development | Testing | Documentation | Planning | Progress |
| --- | --- | --- | --- | --- | --- | --- |
| TaskA | d | d | t | doc | plan | 100% |
""".strip(),
    )
    schema = _write(
        tmp_path / "schema.json",
        json.dumps({"type": "object", "additionalProperties": {"type": "integer"}}),
    )
    index = tmp_path / "status_index.json"

    drift = reconciler.reconcile(
        phase5_path=phase5,
        stubs_path=stubs,
        schema_path=schema,
        index_path=index,
        check=False,
    )
    assert drift == {}
    assert json.loads(index.read_text()) == {"TaskA": 100}


def test_reconcile_drift(tmp_path: Path) -> None:
    phase5 = _write(
        tmp_path / "PHASE5_TASKS_STARTED.md",
        """
## 1. TaskA
- [ ] **Progress:** 50%
""".strip(),
    )
    stubs = _write(
        tmp_path / "task_stubs.md",
        """
| Task | Design | Development | Testing | Documentation | Planning | Progress |
| --- | --- | --- | --- | --- | --- | --- |
| TaskA | d | d | t | doc | plan | 40% |
""".strip(),
    )
    schema = _write(
        tmp_path / "schema.json",
        json.dumps({"type": "object", "additionalProperties": {"type": "integer"}}),
    )
    index = tmp_path / "status_index.json"

    with pytest.raises(SystemExit):
        reconciler.reconcile(
            phase5_path=phase5,
            stubs_path=stubs,
            schema_path=schema,
            index_path=index,
            check=True,
        )
