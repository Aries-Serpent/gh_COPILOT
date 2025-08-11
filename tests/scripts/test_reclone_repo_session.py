"""Session lifecycle tests for scripts/reclone_repo.py."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest


class _ComplianceModule(types.ModuleType):
    MAX_DEPTH = 5

    def anti_recursion_guard(self, func):
        depth = {"n": 0}

        def wrapper(*args, **kwargs):
            depth["n"] += 1
            if depth["n"] > self.MAX_DEPTH:
                raise RuntimeError("Recursion depth exceeded")
            try:
                return func(*args, **kwargs)
            finally:
                depth["n"] -= 1

        return wrapper

    @staticmethod
    def validate_enterprise_operation(target_path: str | None = None, *, command: str | None = None) -> bool:
        if command and "rm -rf" in command.lower():
            return False
        return True


sys.modules.setdefault("enterprise_modules.compliance", _ComplianceModule("enterprise_modules.compliance"))
class _Tqdm:
    def __init__(self, *args, **kwargs):
        self.iterable = args[0] if args else None

    def __iter__(self):
        return iter(self.iterable or [])

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def update(self, *args, **kwargs) -> None:
        return None


sys.modules.setdefault("tqdm", types.SimpleNamespace(tqdm=_Tqdm))


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "reclone_repo.py"
rr = _load_module(SCRIPT_PATH)


def _args(tmp_path: Path) -> types.SimpleNamespace:
    return types.SimpleNamespace(
        repo_url="url",
        dest=str(tmp_path / "clone"),
        branch="main",
        backup_existing=False,
        clean=False,
    )


def test_session_logged_on_success(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(rr, "parse_args", lambda: _args(tmp_path))
    monkeypatch.setattr(rr, "ensure_git_installed", lambda: None)
    monkeypatch.setattr(rr, "validate_paths", lambda *a, **k: None)
    monkeypatch.setattr(rr, "validate_enterprise_operation", lambda *a, **k: True)
    monkeypatch.setattr(rr, "clone_repository", lambda *a, **k: "commit")

    starts: list[tuple[str | None]] = []
    ends: list[tuple[str, str | None]] = []
    monkeypatch.setattr(rr, "start_session", lambda sid, workspace=None: starts.append((sid, workspace)))
    monkeypatch.setattr(
        rr,
        "end_session",
        lambda sid, *, status, workspace=None: ends.append((sid, status, workspace)),
    )

    rr.main()
    assert len(starts) == 1
    assert len(ends) == 1
    assert ends[0][1] == "success"


def test_session_logged_on_failure(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(rr, "parse_args", lambda: _args(tmp_path))
    monkeypatch.setattr(rr, "ensure_git_installed", lambda: None)
    monkeypatch.setattr(rr, "validate_paths", lambda *a, **k: None)
    monkeypatch.setattr(rr, "validate_enterprise_operation", lambda *a, **k: True)
    monkeypatch.setattr(rr, "clone_repository", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))

    starts: list[tuple[str | None]] = []
    ends: list[tuple[str, str | None]] = []
    monkeypatch.setattr(rr, "start_session", lambda sid, workspace=None: starts.append((sid, workspace)))
    monkeypatch.setattr(
        rr,
        "end_session",
        lambda sid, *, status, workspace=None: ends.append((sid, status, workspace)),
    )

    with pytest.raises(SystemExit):
        rr.main()
    assert len(starts) == 1
    assert len(ends) == 1
    assert ends[0][1] == "failure"
