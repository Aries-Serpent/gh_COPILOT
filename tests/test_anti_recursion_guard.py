import threading
import time
import importlib
import sqlite3
import sys
import types

import py7zr
import pytest

from enterprise_modules import compliance
from utils.validation_utils import anti_recursion_guard
import utils.validation_utils as validation_utils_module
from scripts.validation.semantic_search_reference_validator import (
    validate_no_recursive_folders,
)


def test_guard_prevents_direct_recursion():
    calls = []

    @anti_recursion_guard
    def recurse(n: int) -> int:
        calls.append(n)
        if n > 0:
            recurse(n - 1)
        return len(calls)

    with pytest.raises(RuntimeError):
        recurse(1)


def test_guard_via_multiple_import_paths():
    @anti_recursion_guard
    def first():
        second()

    @validation_utils_module.anti_recursion_guard
    def second():
        first()

    with pytest.raises(RuntimeError):
        first()


def test_guard_applied_to_backup_archiver(monkeypatch, tmp_path):
    dummy_compliance = types.ModuleType("enterprise_modules.compliance")
    dummy_compliance.validate_enterprise_operation = lambda path: True
    sys.modules["enterprise_modules.compliance"] = dummy_compliance
    backup_archiver = importlib.import_module("scripts.backup_archiver")
    archive_backups = backup_archiver.archive_backups
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    backup_root = tmp_path / "backups"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    class Dummy:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            time.sleep(0.2)
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def write(self, *args, **kwargs):
            pass

    monkeypatch.setattr(py7zr, "SevenZipFile", Dummy)

    t = threading.Thread(target=archive_backups)
    t.start()
    time.sleep(0.05)
    with pytest.raises(RuntimeError):
        archive_backups()
    t.join()


def test_guard_applied_to_semantic_validator(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    def slow_walk(path):
        time.sleep(0.2)
        return []

    monkeypatch.setattr("scripts.validation.semantic_search_reference_validator.os.walk", slow_walk)

    t = threading.Thread(target=validate_no_recursive_folders)
    t.start()
    time.sleep(0.05)
    with pytest.raises(RuntimeError):
        validate_no_recursive_folders()
    t.join()


def test_detect_recursion_records_pid_for_nested_paths(monkeypatch, tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    nested = root / "root"
    nested.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(root))

    assert compliance._detect_recursion(root) is True

    with sqlite3.connect(root / "databases" / "analytics.db") as conn:
        rows = conn.execute("SELECT path, pid FROM recursion_pid_log").fetchall()

    paths = {row[0] for row in rows}
    assert str(root.resolve()) in paths
    assert str(nested.resolve()) in paths
    pids = {row[1] for row in rows}
    assert compliance._detect_recursion.last_pid in pids


def test_detect_recursion_aborts_on_depth(monkeypatch, tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    current = root
    for i in range(compliance.MAX_RECURSION_DEPTH + 2):
        current = current / f"lvl{i}"
        current.mkdir()

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(root))

    assert compliance._detect_recursion(root) is True
    assert compliance._detect_recursion.aborted is True

    aborted_path = compliance._detect_recursion.aborted_path
    with sqlite3.connect(root / "databases" / "analytics.db") as conn:
        paths = {row[0] for row in conn.execute("SELECT path FROM recursion_pid_log")}

    assert str(root.resolve()) in paths
    assert str(aborted_path.resolve()) in paths
