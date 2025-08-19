"""Tests for docs_status_reconciler."""

from pathlib import Path

import pytest

from scripts import docs_status_reconciler as reconciler


@pytest.mark.skipif(reconciler.yaml is None, reason="PyYAML not installed")
def test_collect_entries(tmp_path: Path) -> None:
    content = (
        "# Phase 5\n\n"
        "### Task One\n"
        "---\n"
        "id: task-one\n"
        "status: started\n"
        "---\n\n"
        "### Task Two\n"
        "---\n"
        "id: task-two\n"
        "status: done\n"
        "---\n"
    )
    path = tmp_path / "PHASE5_TASKS_STARTED.md"
    path.write_text(content, encoding="utf-8")

    entries = reconciler._collect_entries(path)
    assert entries == [
        {
            "id": "task-one",
            "status": "started",
            "file": "PHASE5_TASKS_STARTED.md#task-one",
        },
        {
            "id": "task-two",
            "status": "done",
            "file": "PHASE5_TASKS_STARTED.md#task-two",
        },
    ]


def test_collect_entries_without_yaml(monkeypatch, tmp_path: Path, caplog) -> None:
    content = (
        "# Phase 5\n\n"
        "### Task\n"
        "---\n"
        "id: task\n"
        "status: started\n"
        "---\n"
    )
    path = tmp_path / "PHASE5_TASKS_STARTED.md"
    path.write_text(content, encoding="utf-8")

    monkeypatch.setattr(reconciler, "yaml", None)
    with caplog.at_level("WARNING"):
        entries = reconciler._collect_entries(path)
    assert entries == []
    assert "PyYAML is not installed" in caplog.text

