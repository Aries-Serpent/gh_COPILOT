import importlib.util
import os
from pathlib import Path
import pytest
import types
import sys


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


dummy_worker = types.SimpleNamespace(
    encoding_successful=type("Sig", (), {"connect": lambda self, cb: None})(),
    run_encode=lambda self: None,
)
sys.modules.setdefault(
    "misc.legacy.Base64ImageTransformer",
    types.SimpleNamespace(EncodeWorker=lambda *_a, **_k: dummy_worker),
)
sys.modules.setdefault("tqdm", types.SimpleNamespace(tqdm=lambda x: x))

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

compliance_stub = _ComplianceModule("enterprise_modules.compliance")
sys.modules.setdefault("enterprise_modules.compliance", compliance_stub)
sys.modules.setdefault(
    "scripts.run_migrations", types.SimpleNamespace(ensure_migrations_applied=lambda: None)
)

b2b = _load_module(Path(__file__).resolve().parents[2] / "scripts" / "binary_to_base64.py")
rr = _load_module(Path(__file__).resolve().parents[2] / "scripts" / "reclone_repo.py")


def _setup_env(tmp_path):
    workspace = tmp_path / "ws"
    backup = tmp_path / "backup"
    workspace.mkdir()
    backup.mkdir()
    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(backup)
    return workspace


def test_run_git_blocks_forbidden_command(monkeypatch, tmp_path):
    _setup_env(tmp_path)
    monkeypatch.setattr(b2b.subprocess, "run", lambda *a, **k: None)
    with pytest.raises(RuntimeError):
        b2b.run_git("rm", "-rf", "/")


def test_clone_repository_recursion(monkeypatch, tmp_path):
    workspace = _setup_env(tmp_path)

    monkeypatch.setattr(rr, "validate_enterprise_operation", lambda *a, **k: True)

    def fake_run(*args, **kwargs):
        rr.clone_repository("url", str(workspace / "dest"), "main")

    monkeypatch.setattr(rr.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError):
        rr.clone_repository("url", str(workspace / "dest"), "main")
