import importlib.util
import sys
from pathlib import Path


def test_setup_environment_imports_utils(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(tmp_path)
    # remove repo_root from sys.path to simulate execution outside workspace
    cleaned_paths = []
    for p in list(sys.path):
        try:
            if Path(p).resolve() != repo_root:
                cleaned_paths.append(p)
        except Exception:
            continue
    monkeypatch.setattr(sys, "path", cleaned_paths)

    spec = importlib.util.spec_from_file_location("setup_environment", repo_root / "scripts" / "setup_environment.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert "utils.validation_utils" in sys.modules
