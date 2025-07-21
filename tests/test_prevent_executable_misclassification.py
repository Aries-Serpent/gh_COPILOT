import importlib.util
from pathlib import Path
import pytest

from scripts.orchestrators.unified_wrapup_orchestrator import (
    UnifiedWrapUpOrchestrator,
)


def test_classify_python(tmp_path: Path) -> None:
    path = tmp_path / "run.PY"
    path.write_text("print('hi')")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "python"


def test_detect_python_shebang(tmp_path: Path) -> None:
    path = tmp_path / "script.sh"
    path.write_text("#!/usr/bin/env python\nprint('hi')")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "python"


def test_classify_shell(tmp_path: Path) -> None:
    path = tmp_path / "deploy.sh"
    path.write_text("#!/bin/sh")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "shell"


def test_classify_shell_shebang_txt(tmp_path: Path) -> None:
    path = tmp_path / "foo.txt"
    path.write_text("#!/bin/bash\necho hi")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    with pytest.raises(ValueError):
        orchestrator.prevent_executable_misclassification(path)


def test_classify_batch(tmp_path: Path) -> None:
    path = tmp_path / "build.BAT"
    path.write_text("echo off")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "batch"


def test_classify_psm1(tmp_path: Path) -> None:
    path = tmp_path / "module.psm1"
    path.write_text("Write-Host hello")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "shell"


def test_detect_pyc(tmp_path: Path) -> None:
    path = tmp_path / "module.pyc"
    with open(path, "wb") as f:
        f.write(importlib.util.MAGIC_NUMBER + b"0000")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "python"


def test_classify_unknown(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("abc")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "unknown"


def test_classify_javascript(tmp_path: Path) -> None:
    path = tmp_path / "app.js"
    path.write_text("console.log('hi')")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "javascript"


def test_mismatch_extension(tmp_path: Path) -> None:
    path = tmp_path / "bad.txt"
    path.write_text("#!/usr/bin/env node\nconsole.log('hi')")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    with pytest.raises(ValueError):
        orchestrator.prevent_executable_misclassification(path)


def test_classify_go(tmp_path: Path) -> None:
    path = tmp_path / "main.go"
    path.write_text("package main")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "go"


def test_classify_rust(tmp_path: Path) -> None:
    path = tmp_path / "lib.rs"
    path.write_text("fn main() {}")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "rust"


def test_classify_c(tmp_path: Path) -> None:
    path = tmp_path / "prog.c"
    path.write_text("int main(){}")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "c"


def test_classify_java(tmp_path: Path) -> None:
    path = tmp_path / "Main.java"
    path.write_text("class Main{}")
    orchestrator = UnifiedWrapUpOrchestrator(workspace_path=str(tmp_path))
    assert orchestrator.prevent_executable_misclassification(path) == "java"
