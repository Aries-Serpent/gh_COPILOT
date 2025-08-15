from pathlib import Path
import importlib.util
import sys
import types


class _TqdmStub:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):  # pragma: no cover - trivial
        return self

    def __exit__(self, *exc):  # pragma: no cover - trivial
        return False

    def update(self, *args, **kwargs):  # pragma: no cover - trivial
        pass


sys.modules.setdefault("tqdm", types.SimpleNamespace(tqdm=_TqdmStub))


def _load_module():
    path = Path(__file__).resolve().parents[2] / "scripts" / "security" / "validator.py"
    spec = importlib.util.spec_from_file_location("validator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_load_security_configs_reads_json_files():
    module = _load_module()
    configs = module.load_security_configs()
    assert "access_control_matrix.json" in configs
    assert "encryption_standards.json" in configs
