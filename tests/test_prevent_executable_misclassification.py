from pathlib import Path

from scripts.orchestrators.unified_wrapup_orchestrator import (
    UnifiedWrapUpOrchestrator,
)


def test_classify_python(tmp_path: Path) -> None:
    path = tmp_path / "run.PY"
    path.write_text("print('hi')")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "python"


def test_classify_shell(tmp_path: Path) -> None:
    path = tmp_path / "deploy.sh"
    path.write_text("#!/bin/sh")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "shell"


def test_classify_batch(tmp_path: Path) -> None:
    path = tmp_path / "build.BAT"
    path.write_text("echo off")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "batch"


def test_classify_unknown(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("abc")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "unknown"
