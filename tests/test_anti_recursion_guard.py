import threading
import time
import importlib
import sys
import types

import py7zr
import pytest

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
