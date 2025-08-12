import importlib
import sys
import types
from pathlib import Path
from unittest import mock

class _DummyTqdm:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def update(self, *args, **kwargs):
        pass

sys.modules.setdefault("tqdm", types.SimpleNamespace(tqdm=_DummyTqdm))
sys.modules.setdefault("scripts.docs_metrics_validator", types.ModuleType("docs_metrics_validator"))
sys.modules.setdefault("scripts.validate_docs_metrics", types.ModuleType("validate_docs_metrics"))
numpy_stub = types.ModuleType("numpy")
numpy_stub.ndarray = object
numpy_stub.lib = types.SimpleNamespace(NumpyVersion=lambda *_: None)
numpy_stub.__version__ = "0"
sys.modules.setdefault("numpy", numpy_stub)
sys.modules.setdefault("psutil", types.ModuleType("psutil"))

sys.modules.setdefault("qiskit", types.ModuleType("qiskit"))

quantum_pkg = types.ModuleType("quantum")
quantum_pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "quantum")]
sys.modules["quantum"] = quantum_pkg
quantum_utils_pkg = types.ModuleType("ghc_quantum.utils")
quantum_utils_pkg.__path__ = []
sys.modules["ghc_quantum.utils"] = quantum_utils_pkg
backend_provider_stub = types.ModuleType("ghc_quantum.utils.backend_provider")
backend_provider_stub.get_backend = lambda *args, **kwargs: None
sys.modules["ghc_quantum.utils.backend_provider"] = backend_provider_stub
algorithms_pkg = types.ModuleType("ghc_quantum.algorithms")
algorithms_base = types.ModuleType("ghc_quantum.algorithms.base")
algorithms_base.TEXT_INDICATORS = {"progress": ""}
sys.modules["ghc_quantum.algorithms"] = algorithms_pkg
sys.modules["ghc_quantum.algorithms.base"] = algorithms_base
qo = importlib.import_module("ghc_quantum.optimizers.quantum_optimizer")


def test_detect_c_temp_violations_docstring():
    doc = qo.detect_c_temp_violations.__doc__
    assert doc and "E:/temp" in doc


def test_detect_c_temp_violations_logs_when_forbidden(tmp_path):
    ws = Path("E:/temp/project")
    bk = tmp_path
    with mock.patch.object(qo.CrossPlatformPathManager, "get_workspace_path", return_value=ws), \
         mock.patch.object(qo.CrossPlatformPathManager, "get_backup_root", return_value=bk), \
         mock.patch.object(qo, "_log_violation") as log:
        assert qo.detect_c_temp_violations() == str(ws)
        log.assert_called_once_with(str(ws))
