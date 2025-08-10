from pathlib import Path

import pytest

from scripts.docs_status_reconciler import generate_status_index


def test_generate_status_index(tmp_path: Path, monkeypatch):
    stubs = tmp_path / "task_stubs.md"
    stubs.write_text("| Task |\n| --- |\n| Alpha |\n| Beta |\n")
    started = tmp_path / "PHASE5_TASKS_STARTED.md"
    started.write_text("- Alpha\n")

    monkeypatch.setattr("scripts.docs_status_reconciler.TASK_STUBS_PATH", stubs)
    monkeypatch.setattr("scripts.docs_status_reconciler.TASKS_STARTED_PATH", started)

    index = generate_status_index()
    assert index == {"Alpha": True, "Beta": False}


def test_unknown_task_raises(tmp_path: Path, monkeypatch):
    stubs = tmp_path / "task_stubs.md"
    stubs.write_text("| Task |\n| --- |\n| Alpha |\n")
    started = tmp_path / "PHASE5_TASKS_STARTED.md"
    started.write_text("- Beta\n")

    monkeypatch.setattr("scripts.docs_status_reconciler.TASK_STUBS_PATH", stubs)
    monkeypatch.setattr("scripts.docs_status_reconciler.TASKS_STARTED_PATH", started)

    with pytest.raises(ValueError):
        generate_status_index()
